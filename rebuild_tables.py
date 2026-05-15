"""重建表（当前版本），与数据库实际结构保持一致。"""
import pymysql

DEST = dict(host="127.0.0.1", user="root", password="0826", database="hainan_41811", charset="utf8mb4")
conn = pymysql.connect(**DEST)
cur = conn.cursor()

# 先禁用外键检查，再删除所有表
cur.execute("SET FOREIGN_KEY_CHECKS = 0")
for t in [
    "indicator_execution", "indicator",
    "core18_execution_log", "core18_indicator",
    "personnel_violation", "institution_anomaly",
    "technology_warning", "equipment_anomaly",
    "four_elements_monitoring_record",
    "hospital",
    "table_metadata", "column_metadata",
    "user", "hospital_admission_standard", "text2sql_log",
    "dashboard_alert", "dashboard_statistics",
]:
    cur.execute(f"DROP TABLE IF EXISTS {t}")
cur.execute("SET FOREIGN_KEY_CHECKS = 1")
conn.commit()

# user
cur.execute("""
CREATE TABLE `user` (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    real_name VARCHAR(100),
    role VARCHAR(50),
    scope_type VARCHAR(20),
    scope_hospital_id VARCHAR(50),
    is_active TINYINT(1) DEFAULT 1,
    created_at DATETIME,
    updated_at DATETIME
)
""")

# hospital
cur.execute("""
CREATE TABLE hospital (
    id VARCHAR(50) PRIMARY KEY,
    hospital_code VARCHAR(50),
    name VARCHAR(200) NOT NULL,
    level VARCHAR(20),
    hospital_type VARCHAR(20),
    region VARCHAR(100),
    address VARCHAR(300),
    contact VARCHAR(50),
    bed_count INT,
    is_active INT DEFAULT 1,
    created_at DATETIME,
    updated_at DATETIME
)
""")

# indicator
cur.execute("""
CREATE TABLE indicator (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    indicator_type VARCHAR(20),
    category VARCHAR(100),
    seq INT,
    scope TEXT,
    work_content TEXT,
    rule_logic TEXT,
    formula TEXT,
    description TEXT,
    calc_method VARCHAR(20),
    sql_content TEXT,
    prompt_content TEXT,
    involved_tables JSON,
    numerator_desc TEXT,
    denominator_desc TEXT,
    numerator_sql TEXT,
    denominator_sql TEXT,
    status VARCHAR(20),
    is_computable TINYINT(1),
    use_llm TINYINT(1),
    platform_data_ready TINYINT(1),
    priority VARCHAR(20),
    remark TEXT,
    regex_match TINYINT(1),
    regex_rule TEXT,
    calc_type VARCHAR(20),
    created_at DATETIME,
    updated_at DATETIME
)
""")

# indicator_execution
cur.execute("""
CREATE TABLE indicator_execution (
    id INT PRIMARY KEY AUTO_INCREMENT,
    indicator_id INT,
    indicator_name VARCHAR(200),
    execution_type VARCHAR(20),
    kind VARCHAR(20),
    run_mode VARCHAR(20),
    time_range VARCHAR(50),
    result_type VARCHAR(20),
    calc_method VARCHAR(20),
    scope VARCHAR(50),
    logs JSON,
    numerator_sql TEXT,
    denominator_sql TEXT,
    `sql` TEXT,
    numerator_count INT,
    denominator_count INT,
    rate_percent DOUBLE,
    rate_formula VARCHAR(200),
    result_text TEXT,
    preview_data JSON,
    denominator_preview_data JSON,
    error TEXT,
    numerator_error TEXT,
    denominator_error TEXT,
    attempts JSON,
    llm_thinking TEXT,
    llm_raw TEXT,
    cache_hit TINYINT(1),
    request_id VARCHAR(100),
    conversation_id VARCHAR(100),
    status VARCHAR(20),
    execution_time DATETIME,
    duration_seconds DOUBLE
)
""")

# core18_indicator
cur.execute("""
CREATE TABLE core18_indicator (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100),
    seq INT,
    scope TEXT,
    work_content TEXT,
    rule_logic TEXT,
    formula TEXT,
    description TEXT,
    calc_method VARCHAR(20),
    sql_content TEXT,
    prompt_content TEXT,
    involved_tables JSON,
    numerator_desc TEXT,
    denominator_desc TEXT,
    numerator_sql TEXT,
    denominator_sql TEXT,
    status VARCHAR(20),
    is_computable TINYINT(1),
    use_llm TINYINT(1),
    priority VARCHAR(20),
    remark TEXT,
    created_at DATETIME,
    updated_at DATETIME
)
""")

# core18_execution_log
cur.execute("""
CREATE TABLE core18_execution_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    indicator_id INT,
    indicator_name VARCHAR(200),
    execution_type VARCHAR(20),
    run_mode VARCHAR(20),
    time_range VARCHAR(50),
    result_type VARCHAR(20),
    calc_method VARCHAR(20),
    scope VARCHAR(50),
    logs JSON,
    numerator_sql TEXT,
    denominator_sql TEXT,
    `sql` TEXT,
    numerator_count INT,
    denominator_count INT,
    rate_percent DOUBLE,
    rate_formula VARCHAR(200),
    result_text TEXT,
    preview_data JSON,
    denominator_preview_data JSON,
    error TEXT,
    numerator_error TEXT,
    denominator_error TEXT,
    attempts JSON,
    llm_thinking TEXT,
    llm_raw TEXT,
    cache_hit TINYINT(1),
    request_id VARCHAR(100),
    conversation_id VARCHAR(100),
    status VARCHAR(20),
    execution_time DATETIME,
    duration_seconds DOUBLE
)
""")

# four_elements_monitoring_record（不含 department_id）
cur.execute("""
CREATE TABLE four_elements_monitoring_record (
    id INT PRIMARY KEY AUTO_INCREMENT,
    hospital_id VARCHAR(50),
    factor VARCHAR(20) NOT NULL,
    record_type VARCHAR(100),
    title VARCHAR(200),
    description TEXT,
    severity VARCHAR(20),
    status VARCHAR(20),
    alert_time DATETIME,
    resolved_time DATETIME,
    handler VARCHAR(100),
    handler_comment TEXT,
    related_indicator_id INT,
    extra_data JSON
)
""")

# personnel_violation
cur.execute("""
CREATE TABLE personnel_violation (
    id INT PRIMARY KEY AUTO_INCREMENT,
    record_id INT,
    physician_name VARCHAR(100),
    physician_id VARCHAR(50),
    violation_type VARCHAR(50),
    violation_details TEXT,
    prescription_count INT,
    distance_traveled DOUBLE,
    time_window INT
)
""")

# institution_anomaly
cur.execute("""
CREATE TABLE institution_anomaly (
    id INT PRIMARY KEY AUTO_INCREMENT,
    record_id INT,
    anomaly_type VARCHAR(50),
    anomaly_details TEXT,
    threshold_value INT,
    actual_value INT,
    excess_percent DOUBLE
)
""")

# technology_warning
cur.execute("""
CREATE TABLE technology_warning (
    id INT PRIMARY KEY AUTO_INCREMENT,
    record_id INT,
    warning_type VARCHAR(50),
    warning_details TEXT,
    patient_name VARCHAR(100),
    patient_id VARCHAR(50),
    risk_level VARCHAR(20)
)
""")

# equipment_anomaly
cur.execute("""
CREATE TABLE equipment_anomaly (
    id INT PRIMARY KEY AUTO_INCREMENT,
    record_id INT,
    equipment_name VARCHAR(200),
    equipment_code VARCHAR(50),
    anomaly_type VARCHAR(50),
    anomaly_details TEXT,
    positive_rate DOUBLE,
    usage_hours DOUBLE
)
""")

# table_metadata
cur.execute("""
CREATE TABLE table_metadata (
    id INT PRIMARY KEY AUTO_INCREMENT,
    table_name VARCHAR(100) UNIQUE NOT NULL,
    business_definition TEXT,
    data_granularity TEXT,
    remarks TEXT,
    field_count INT,
    formatted_text TEXT,
    last_synced DATETIME,
    source VARCHAR(50)
)
""")

# column_metadata
cur.execute("""
CREATE TABLE column_metadata (
    id INT PRIMARY KEY AUTO_INCREMENT,
    table_id INT,
    field_name VARCHAR(100) NOT NULL,
    data_type VARCHAR(50),
    meaning_cn VARCHAR(500),
    field_constraint TEXT
)
""")

# hospital_admission_standard
cur.execute("""
CREATE TABLE hospital_admission_standard (
    id INT PRIMARY KEY AUTO_INCREMENT,
    standard_code VARCHAR(100) UNIQUE NOT NULL,
    standard_name VARCHAR(300) NOT NULL,
    category VARCHAR(100),
    `level` VARCHAR(20),
    requirement TEXT,
    documents_needed JSON,
    check_items JSON,
    pass_threshold VARCHAR(200),
    status VARCHAR(20),
    approved_hospital_id VARCHAR(50),
    approved_hospital_name VARCHAR(200),
    approved_date DATE,
    expiry_date DATE,
    license_no VARCHAR(100),
    license_front_image VARCHAR(500),
    license_back_image VARCHAR(500),
    other_images JSON,
    remark TEXT,
    created_at DATETIME,
    updated_at DATETIME
)
""")

# text2sql_log
cur.execute("""
CREATE TABLE text2sql_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    user_question TEXT,
    generated_sql TEXT,
    sql_valid TINYINT(1),
    sql_error TEXT,
    execution_time DATETIME,
    duration_ms INT,
    selected_tables JSON,
    llm_model VARCHAR(100),
    request_id VARCHAR(100),
    session_id VARCHAR(100),
    status VARCHAR(20),
    result_preview JSON,
    result_count INT,
    indicator_name VARCHAR(200),
    indicator_type VARCHAR(50)
)
""")

conn.commit()
conn.close()
print("表重建完成！")
