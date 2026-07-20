import re
from typing import Any

try:
    import spacy
except ImportError:  # pragma: no cover
    spacy = None


class EntityExtractor:
    def __init__(self) -> None:
        self.nlp = None
        if spacy is not None:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                self.nlp = spacy.blank("en")

    def extract(self, text: str) -> dict[str, Any]:
        cleaned_text = text or ""
        name = self._extract_name(cleaned_text)
        email = self._extract_email(cleaned_text)
        phone = self._extract_phone(cleaned_text)
        address = self._extract_location(cleaned_text)
        linkedin = self._extract_link(cleaned_text, "linkedin.com")
        github = self._extract_link(cleaned_text, "github.com")
        portfolio = self._extract_portfolio(cleaned_text)
        education = self._extract_education(cleaned_text)
        skills = self._extract_skills(cleaned_text)
        experience = self._extract_experience(cleaned_text)
        projects = self._extract_projects(cleaned_text)
        certifications = self._extract_certifications(cleaned_text)
        languages = self._extract_languages(cleaned_text)
        return {
            "name": name,
            "email": email,
            "phone": phone,
            "address": address,
            "linkedin": linkedin,
            "github": github,
            "portfolio": portfolio,
            "education": education,
            "skills": skills,
            "experience_years": experience,
            "projects": projects,
            "certifications": certifications,
            "languages": languages,
        }

    def _extract_name(self, text: str) -> str | None:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return None
        first_line = lines[0]
        if re.search(r"@", first_line):
            return None
        return first_line[:100]

    def _extract_email(self, text: str) -> str | None:
        match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
        return match.group(0) if match else None

    def _extract_phone(self, text: str) -> str | None:
        cleaned_text = text or ""
        candidates = re.findall(r"(?:\+91|91|0)?[\s\-\.]*\(?\d{2,4}\)?[\s\-\.]*\d{3}[\s\-\.]*\d{4}", cleaned_text)
        for candidate in candidates:
            digits = re.sub(r"\D", "", candidate)
            if digits.startswith("91") and len(digits) > 10:
                digits = digits[2:]
            elif digits.startswith("0") and len(digits) > 10:
                digits = digits[1:]
            if len(digits) == 10:
                return digits
        # fallback: first 10-digit substring in raw text
        all_digits = re.sub(r"\D", "", cleaned_text)
        for i in range(len(all_digits) - 9):
            segment = all_digits[i:i + 10]
            if len(segment) == 10:
                return segment
        return None

    def _extract_location(self, text: str) -> str | None:
        """Extract a candidate city from common resume headers and labels."""
        cities = (
            "Ahmedabad", "Bengaluru", "Bangalore", "Bhopal", "Chennai", "Coimbatore",
            "Delhi", "Gurgaon", "Gurugram", "Hyderabad", "Indore", "Jaipur", "Kochi",
            "Kolkata", "Lucknow", "Mumbai", "Mysuru", "Nagpur", "Noida", "Pune",
            "Thiruvananthapuram", "Visakhapatnam",
        )
        header = "\n".join(text.splitlines()[:12])
        labelled = re.search(r"(?:location|address|city|based\s+in)\s*[:\-]?\s*([A-Za-z ]{3,80})", header, re.IGNORECASE)
        search_text = labelled.group(1) if labelled else header
        for city in cities:
            if re.search(rf"\b{re.escape(city)}\b", search_text, re.IGNORECASE):
                return city
        return None

    def _extract_link(self, text: str, domain: str) -> str | None:
        pattern = rf"(?:https?://)?(?:www\.)?{re.escape(domain)}/[A-Za-z0-9_\-/.]+"
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            return None
        found = match.group(0).rstrip(").,;:")
        if not re.match(r"https?://", found, re.IGNORECASE):
            found = f"https://{found}"
        return found

    def _extract_portfolio(self, text: str) -> str | None:
        # Explicit "Portfolio:" / "Website:" labels first (most reliable)
        label_match = re.search(
            r"(?:portfolio|website|personal\s+site)\s*[:\-]?\s*((?:https?://)?(?:www\.)?[A-Za-z0-9\-]+\.[A-Za-z]{2,}(?:/[A-Za-z0-9_\-/.]*)?)",
            text,
            re.IGNORECASE,
        )
        if label_match:
            url = label_match.group(1).rstrip(").,;:")
            if not re.match(r"https?://", url, re.IGNORECASE):
                url = f"https://{url}"
            return url
        return None

    # Section headers used to isolate the Education block from the rest of
    # the resume. Without this isolation, degree keywords like "BE" or
    # "MBA" can accidentally match substrings buried in unrelated text
    # elsewhere in the document (e.g. "BERT", "benchmarked", "Coimbatore"
    # all contain "be"/"mba" as substrings) - which was the root cause of
    # garbage/duplicate education rows and misattributed CGPA/year/college.
    _EDUCATION_HEADER_NAMES = {"education"}
    _NEXT_SECTION_HEADER_NAMES = {
        "technical skills",
        "skills",
        "projects",
        "certifications",
        "experience",
        "work experience",
        "achievements",
        "additional information",
        "areas of interest",
        "soft skills",
        "languages",
    }

    def _extract_education(self, text: str) -> list[dict[str, Any]]:
        lines = [line.strip() for line in (text or "").splitlines()]

        # 1. Isolate the Education section only (from the "Education"
        # header line to the next recognized section header). This is what
        # prevents unrelated resume sections (Projects, Certifications,
        # etc.) from ever being scanned for degree keywords at all.
        start_idx = None
        for i, line in enumerate(lines):
            if line.strip().lower() in self._EDUCATION_HEADER_NAMES:
                start_idx = i + 1
                break
        if start_idx is None:
            return []

        end_idx = len(lines)
        for i in range(start_idx, len(lines)):
            if lines[i].strip().lower() in self._NEXT_SECTION_HEADER_NAMES:
                end_idx = i
                break

        section_lines = [l for l in lines[start_idx:end_idx] if l.strip()]
        if not section_lines:
            return []

        # Degree keywords now use \b word boundaries, so they can only match
        # whole words - "BE" can no longer match inside "BERT", and "MBA"
        # can no longer match inside "Coimbatore".
        degree_pattern = (
            r"\b(B\.?Tech|B\.?E\.?|M\.?Tech|MBA|B\.?Sc|M\.?Sc|BCA|MCA|Ph\.?D"
            r"|Bachelor(?:'s)?(?:\s+of\s+[A-Za-z]+)?|Master(?:'s)?(?:\s+of\s+[A-Za-z]+)?|Diploma)\b"
        )
        college_keyword_pattern = r"(University|College|Institute|Vidyapeetham|Academy|Polytechnic|School)"
        cgpa_pattern = r"(?:CGPA|GPA)\s*[:\-]?\s*(\d{1,2}(?:\.\d{1,2})?)"
        year_pattern = r"\b(?:19|20)\d{2}\b"

        # 2. Group lines into per-institution blocks. A new block starts at
        # any line that looks like an institution name (contains a
        # recognized college/university keyword), so each degree/CGPA/year
        # only ever gets matched against text belonging to ITS OWN
        # institution, never a neighboring one.
        blocks: list[list[str]] = []
        current: list[str] = []
        for line in section_lines:
            if re.search(college_keyword_pattern, line, re.IGNORECASE) and current:
                blocks.append(current)
                current = [line]
            else:
                current.append(line)
        if current:
            blocks.append(current)

        results: list[dict[str, Any]] = []
        for block in blocks:
            degree = None
            degree_line = None
            degree_match = None
            for line in block:
                m = re.search(degree_pattern, line, re.IGNORECASE)
                if m:
                    degree = m.group(0)
                    degree_line = line
                    degree_match = m
                    break
            if not degree:
                # No formal degree found in this block (e.g. schooling
                # entries like "Class X" / "Class XII") - skip rather than
                # guessing, instead of misreporting it as a degree.
                continue

            college = None
            for line in block:
                cmatch = re.search(
                    rf"([A-Z][A-Za-z0-9&.'\- ]*?{college_keyword_pattern}[A-Za-z0-9&.'\- ]*)",
                    line,
                    re.IGNORECASE,
                )
                if cmatch:
                    college = cmatch.group(1).strip(" ,-")
                    break

            branch = None
            after_degree = degree_line[degree_match.end():]
            branch_match = re.match(
                r"\s*(?:in|:|-)?\s*([A-Za-z&][A-Za-z&\s–-]{2,80}?)"
                r"(?=\s{2,}|,|\b(?:19|20)\d{2}\b|$)",
                after_degree,
                re.IGNORECASE,
            )
            if branch_match:
                candidate_branch = branch_match.group(1).strip(" ,-–")
                if candidate_branch and not re.search(college_keyword_pattern, candidate_branch, re.IGNORECASE):
                    branch = candidate_branch

            cgpa = None
            cgpa_match = re.search(cgpa_pattern, "\n".join(block), re.IGNORECASE)
            if cgpa_match:
                cgpa = cgpa_match.group(1)

            # Graduation year: prefer the last year on the degree's own
            # line (handles "2023 – 2027" ranges by taking the later
            # year), falling back to the institution line only if the
            # degree line itself has no year at all.
            graduation_year = None
            year_matches = re.findall(year_pattern, degree_line)
            if not year_matches:
                year_matches = re.findall(year_pattern, block[0])
            if year_matches:
                graduation_year = year_matches[-1]

            results.append(
                {
                    "degree": degree,
                    "college": college,
                    "branch": branch,
                    "cgpa": cgpa,
                    "graduation_year": graduation_year,
                }
            )

        return results[:5]

    def _extract_skills(self, text: str) -> list[str]:
        skills = [
            "Python",
            "Java",
            "JavaScript",
            "TypeScript",
            "SQL",
            "FastAPI",
            "React",
            "AWS",
            "Docker",
            "Azure",
            "Machine Learning",
            "Data Science",
            "Spring Boot",
            "Node.js",
            "C++",
            "C#",
            "Kubernetes",
        ]
        found = []
        for skill in skills:
            if re.search(rf"\b{re.escape(skill)}\b", text, re.IGNORECASE):
                found.append(skill)
        return found

    def _extract_experience(self, text: str) -> str | None:
        year_matches = re.findall(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\b", text, re.IGNORECASE)
        if year_matches:
            return str(max(float(value) for value in year_matches)).rstrip("0").rstrip(".")
        month_matches = re.findall(r"(\d+)\s*\+?\s*months?\b", text, re.IGNORECASE)
        if month_matches:
            return str(round(max(int(value) for value in month_matches) / 12, 1))
        return "0"

    def _extract_projects(self, text: str) -> list[dict[str, str]]:
        projects = []
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        for line in lines:
            if re.search(r"project|built|developed|implemented", line, re.IGNORECASE):
                projects.append({"title": line[:100], "description": line})
        return projects[:5]

    def _extract_certifications(self, text: str) -> list[dict[str, str]]:
        certs = []
        for line in text.splitlines():
            if re.search(r"certification|certified|aws|azure|oracle|ccna", line, re.IGNORECASE):
                clean_line = re.sub(r"\s*\(cid:\d+\)", "", line, flags=re.IGNORECASE).strip()
                certs.append({"certificate_name": clean_line[:100]})
        return certs[:5]

    def _extract_languages(self, text: str) -> list[str]:
        languages = ["English", "Hindi", "Tamil", "Telugu", "Kannada", "Marathi", "Spanish", "German"]
        found = []
        for language in languages:
            if re.search(rf"\b{re.escape(language)}\b", text, re.IGNORECASE):
                found.append(language)
        return found
