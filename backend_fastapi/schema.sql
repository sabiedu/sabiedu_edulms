-- EduLMS v2 Database Schema for TiDB Serverless
-- Generated from SQLAlchemy models

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS edulms_v2;
USE edulms_v2;

-- Users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    
    -- Profile information
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    avatar_url VARCHAR(255),
    bio TEXT,
    
    -- User preferences
    learning_style VARCHAR(20) DEFAULT 'visual',
    preferred_language VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'UTC',
    
    -- Agent session tracking
    current_agent_session VARCHAR(100),
    
    -- Status and tracking
    role VARCHAR(20) DEFAULT 'student',
    is_active BOOLEAN DEFAULT TRUE,
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_is_active (is_active)
);

-- Workflows table
CREATE TABLE workflows (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Workflow execution
    status ENUM('pending', 'running', 'completed', 'failed', 'cancelled') DEFAULT 'pending',
    template_name VARCHAR(50),
    
    -- Parameters and results
    parameters JSON,
    results JSON,
    error_message TEXT,
    
    -- Progress tracking
    progress FLOAT DEFAULT 0.0,
    steps_completed INT DEFAULT 0,
    total_steps INT DEFAULT 0,
    
    -- User association
    user_id INT NOT NULL,
    
    -- Timestamps
    started_at DATETIME,
    completed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_status (status),
    INDEX idx_user_id (user_id),
    INDEX idx_template_name (template_name),
    INDEX idx_created_at (created_at)
);

-- Analytics table
CREATE TABLE analytics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    
    -- Event information
    action_type VARCHAR(50) NOT NULL,
    event_category VARCHAR(50),
    
    -- User association
    user_id INT NOT NULL,
    session_id VARCHAR(100),
    
    -- Context
    course_id INT,
    lesson_id INT,
    workflow_id INT,
    agent_session_id VARCHAR(100),
    
    -- Data
    event_metadata JSON,
    performance_score FLOAT,
    duration INT,
    
    -- Tracking
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE SET NULL,
    INDEX idx_action_type (action_type),
    INDEX idx_event_category (event_category),
    INDEX idx_user_id (user_id),
    INDEX idx_session_id (session_id),
    INDEX idx_timestamp (timestamp)
);

-- Content table with vector embeddings
CREATE TABLE content (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content_type VARCHAR(50) NOT NULL,
    
    -- Content data
    content_text TEXT,
    content_metadata JSON,
    
    -- Vector embeddings for TiDB vector search
    embedding VECTOR(768) COMMENT 'Google Gemini embeddings',
    
    -- Content organization
    course_id INT,
    lesson_id INT,
    difficulty_level VARCHAR(20) DEFAULT 'beginner',
    
    -- User association
    created_by INT,
    
    -- Status and tracking
    is_published BOOLEAN DEFAULT FALSE,
    view_count INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_content_type (content_type),
    INDEX idx_course_id (course_id),
    INDEX idx_lesson_id (lesson_id),
    INDEX idx_difficulty_level (difficulty_level),
    INDEX idx_is_published (is_published),
    INDEX idx_created_at (created_at),
    
    -- Vector index for similarity search
    VECTOR INDEX idx_embedding ((VEC_COSINE_DISTANCE(embedding))) COMMENT 'Vector index for semantic search'
);

-- Agent Sessions table
CREATE TABLE agent_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    
    -- Session data
    session_data JSON,
    
    -- User association
    user_id INT NOT NULL,
    
    -- Status tracking
    status VARCHAR(20) DEFAULT 'active',
    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_session_id (session_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_last_activity (last_activity)
);



-- Create additional indexes for performance
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_workflows_completed_at ON workflows(completed_at);
CREATE INDEX idx_analytics_performance_score ON analytics(performance_score);
CREATE INDEX idx_content_view_count ON content(view_count);

-- Sample data for testing (optional)
INSERT INTO users (username, email, password_hash, first_name, last_name, role) VALUES
('admin', 'admin@edulms.com', '$2b$12$example_hash', 'Admin', 'User', 'admin'),
('student1', 'student1@edulms.com', '$2b$12$example_hash', 'John', 'Doe', 'student'),
('teacher1', 'teacher1@edulms.com', '$2b$12$example_hash', 'Jane', 'Smith', 'teacher');

-- Create workflow templates data
INSERT INTO workflows (name, description, template_name, user_id, status) VALUES
('Adaptive Learning Pipeline', 'Personalized learning path generation', 'adaptive_learning_pipeline', 1, 'pending'),
('Content Discovery Workflow', 'AI-powered content recommendation', 'content_discovery_workflow', 1, 'pending'),
('Assessment Generation', 'Automated quiz and test creation', 'assessment_generation_workflow', 1, 'pending');
