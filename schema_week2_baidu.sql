USE learn_db;

DROP TABLE IF EXISTS baidu_hot;
CREATE TABLE baidu_hot (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  rank_no INT NOT NULL,
  title VARCHAR(255) NOT NULL,
  heat VARCHAR(50),
  url VARCHAR(500),
  summary TEXT,
  snapshot_date DATE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uniq_rank_date (rank_no, snapshot_date)
);
