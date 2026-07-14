CREATE DATABASE IF NOT EXISTS recruitment_ai;
USE recruitment_ai;

CREATE TABLE IF NOT EXISTS recruiters (
  id VARCHAR(36) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255),
  google_id VARCHAR(255),
  role VARCHAR(50) DEFAULT 'recruiter',
  is_active BOOLEAN DEFAULT TRUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS candidates (
  candidate_id VARCHAR(36) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255),
  phone VARCHAR(50),
  linkedin VARCHAR(500),
  github VARCHAR(500),
  portfolio VARCHAR(500),
  address TEXT,
  resume_file VARCHAR(500),
  experience_years VARCHAR(20),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS education (
  education_id INT AUTO_INCREMENT PRIMARY KEY,
  candidate_id VARCHAR(36) NOT NULL,
  candidate_name VARCHAR(255),
  degree VARCHAR(255),
  college VARCHAR(255),
  branch VARCHAR(255),
  cgpa VARCHAR(50),
  graduation_year VARCHAR(20),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS skills (
  skill_id INT AUTO_INCREMENT PRIMARY KEY,
  candidate_id VARCHAR(36) NOT NULL,
  candidate_name VARCHAR(255),
  skill_name VARCHAR(255) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS projects (
  project_id INT AUTO_INCREMENT PRIMARY KEY,
  candidate_id VARCHAR(36) NOT NULL,
  candidate_name VARCHAR(255),
  title VARCHAR(255) NOT NULL,
  description TEXT,
  technologies VARCHAR(500),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS certifications (
  certificate_id INT AUTO_INCREMENT PRIMARY KEY,
  candidate_id VARCHAR(36) NOT NULL,
  candidate_name VARCHAR(255),
  certificate_name VARCHAR(255) NOT NULL,
  organization VARCHAR(255),
  issue_date VARCHAR(50),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS job (
  job_id VARCHAR(36) PRIMARY KEY,
  job_title VARCHAR(255) NOT NULL,
  company_name VARCHAR(255) NOT NULL,
  description TEXT,
  experience VARCHAR(50),
  location VARCHAR(255),
  salary VARCHAR(50),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
