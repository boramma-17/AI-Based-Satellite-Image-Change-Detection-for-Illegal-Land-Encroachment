-- Drop existing tables safely
DROP TABLE IF EXISTS dbo.detections;
DROP TABLE IF EXISTS dbo.users;

-- Users table: manages system accounts
CREATE TABLE dbo.users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user'
        CHECK (role IN ('user', 'admin', 'researcher')),
    created_at DATETIME NOT NULL DEFAULT GETDATE()
);

-- Detections table: stores satellite image comparisons
CREATE TABLE dbo.detections (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL, -- who uploaded/ran detection
    title VARCHAR(255),   -- optional descriptive title
    before_image VARCHAR(255) NOT NULL, -- path to pre-encroachment image
    after_image VARCHAR(255) NOT NULL,  -- path to post-encroachment image
    result_image VARCHAR(255),          -- path to generated diff/heatmap
    change_percent FLOAT,               -- % change detected
    encroachment_flag BIT NOT NULL DEFAULT 0, -- 1 if illegal encroachment detected
    latitude DECIMAL(9,6),              -- precise location
    longitude DECIMAL(9,6),
    report_path VARCHAR(255),           -- path to generated report file
    created_at DATETIME NOT NULL DEFAULT GETDATE(),

    FOREIGN KEY (user_id)
        REFERENCES dbo.users(id)
        ON DELETE CASCADE
);

-- Index for faster lookups by user
CREATE INDEX idx_detections_user
ON dbo.detections(user_id);

-- Optional: index for geospatial queries
CREATE INDEX idx_detections_location
ON dbo.detections(latitude, longitude);
