USE recruitment_ai;

ALTER TABLE job
ADD COLUMN required_education VARCHAR(255) AFTER required_skills;
