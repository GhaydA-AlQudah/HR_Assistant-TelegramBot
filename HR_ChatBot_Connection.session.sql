DROP TABLE IF EXISTS overtime, leave_balance, leaves, leave_types, payroll, departments, users;



CREATE TABLE departments (
    dep_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    manager_id INTEGER
);

INSERT INTO departments (name) VALUES
('IT'),
('Finance'),
('HR')

--------------------
--------------------


CREATE TABLE users (
    emp_id SERIAL PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) CHECK (role IN ('employee', 'manager', 'hr')),
    job_title VARCHAR(100),
    hire_date DATE,
    salary_basic NUMERIC(10,2),
    dep_id INTEGER,
    telegram_bot_id BIGINT UNIQUE,

    CONSTRAINT fk_user_department
      FOREIGN KEY (dep_id)
      REFERENCES departments(dep_id)
);

INSERT INTO users (
    full_name, email, hashed_password, role, job_title, hire_date, salary_basic, dep_id, telegram_bot_id
) VALUES
('GhaydA Al-Qudah', 'ghayda@bmw.com',
 '$2b$10$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36D1Z5Rk5LZx5F9c3xN6Z6K',
 'manager', 'IT Manager', '2022-01-10', 8000, 1, NULL),

('Sewar Qudah', 'sewar@elite.com',
 '$2b$10$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36D1Z5Rk5LZx5F9c3xN6Z6K',
 'employee', 'AI Engineer', '2023-03-15', 7000, 1, NULL),

('Hosam Qudah', 'husam@pwc.com',
 '$2b$10$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36D1Z5Rk5LZx5F9c3xN6Z6K',
 'manager', 'Accountant', '2021-06-01', 6000, 2, NULL),

('Jameelah Qawaqnah', 'jam@school.com', 
'$2b$10$EixZaYVK1fsbw1ZfbX3OXePaWxn96536D1Z5Rk5LZx5F9c3xN6Z6K',
'hr', 'hr', '2019-05-4', 9000, 3, '8378841110');


UPDATE users 
SET telegram_bot_id = '8378841110' 
WHERE emp_id = 1; 

UPDATE users 
SET telegram_bot_id = '83788741110' 
WHERE emp_id = 4; 


---------------------------
---------------------------


ALTER TABLE departments
ADD CONSTRAINT fk_department_manager
FOREIGN KEY (manager_id)
REFERENCES users(emp_id);

UPDATE departments SET manager_id = 1 WHERE dep_id = 1; -- IT
UPDATE departments SET manager_id = 3 WHERE dep_id = 2; -- Finance
UPDATE departments SET manager_id = 4 WHERE dep_id = 3; -- HR


----------------------------
----------------------------

CREATE TABLE payroll (
    payroll_id SERIAL PRIMARY KEY,
    emp_id INTEGER NOT NULL,
    month INTEGER CHECK (month BETWEEN 1 AND 12),
    year INTEGER,
    basic_salary NUMERIC(10,2),
    allowances NUMERIC(10,2),
    deductions NUMERIC(10,2),
    overtime_amount NUMERIC(10,2),
    net_salary NUMERIC(10,2),
    generated_at TIMESTAMP DEFAULT now(),

    CONSTRAINT fk_payroll_user
      FOREIGN KEY (emp_id) 
      REFERENCES users(emp_id),

    CONSTRAINT uq_user_month 
    UNIQUE (emp_id, month, year)
);


INSERT INTO payroll (
    emp_id, month, year, basic_salary, allowances,
    deductions, overtime_amount, net_salary
) VALUES
(1, 6, 2024, 7000, 500, 200, 350, 7650);

----------------------------
----------------------------

CREATE TABLE leave_types (
    leave_types_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE CHECK (name IN ('ANNUAL', 'SICK', 'CASUAL', 'MATERNITY', 'PATERNITY', 'UNPAID', 'COMP_OFF', 'BEREAVEMENT')),
    default_total_days INTEGER,
    is_paid BOOLEAN DEFAULT TRUE
);

INSERT INTO leave_types (name, default_total_days, is_paid) VALUES
('ANNUAL', 21, TRUE),
('SICK', 10, TRUE),
('CASUAL', 5, True);


-- حذف البيانات القديمة لتجنب التكرار
--TRUNCATE leaves RESTART IDENTITY CASCADE;
TRUNCATE leave_types RESTART IDENTITY CASCADE;

INSERT INTO leave_types (name, default_total_days, is_paid) VALUES
('ANNUAL', 21, TRUE),
('SICK', 15, TRUE),
('CASUAL', 7, TRUE),
('UNPAID', 30, FALSE);

--------------------------------
--------------------------------

CREATE TABLE leaves (
    leave_id SERIAL PRIMARY KEY,
    emp_id INTEGER NOT NULL,
    leave_type_id INTEGER NOT NULL,
    start_date DATE,
    end_date DATE,
    status VARCHAR(50) CHECK (status IN ('pending', 'approved', 'rejected')),
    requested_at TIMESTAMP DEFAULT now(),

    CONSTRAINT fk_leave_user
        FOREIGN KEY (emp_id)
        REFERENCES users(emp_id),

    CONSTRAINT fk_leave_type
        FOREIGN KEY (leave_type_id)
        REFERENCES leave_types(leave_types_id)

);

INSERT INTO leaves (emp_id, leave_type_id, start_date, end_date, status)
VALUES
(1, 1, '2024-05-01', '2024-05-05', 'approved');


INSERT INTO leaves (emp_id, leave_type_id, start_date, end_date, status) VALUES
-- إجازات الموظف رقم 1 (أنتِ)
(1, 1, '2024-01-10', '2024-01-12', 'approved'), -- 3 days - Annual
(1, 1, '2024-03-05', '2024-03-05', 'approved'), -- 1 day - Annual
(1, 2, '2024-02-01', '2024-02-02', 'approved'), -- 2 days - sick
(1, 1, '2024-04-10', '2024-04-12', 'rejected'), -- rejected request - not countable

-- إجازات الموظف رقم 2
(2, 1, '2024-05-01', '2024-05-05', 'approved'), -- 5 days - Annual
(2, 3, '2024-06-01', '2024-06-01', 'pending'),  -- pended request

-- إجازات الموظف رقم 3
(3, 1, '2024-01-15', '2024-01-20', 'approved'),
(3, 2, '2024-02-10', '2024-02-11', 'approved');
----------------------------------
----------------------------------


CREATE TABLE overtime (
    overtime_req_id SERIAL PRIMARY KEY,
    emp_id INTEGER NOT NULL,
    date DATE NOT NULL,
    hours NUMERIC(5,2) CHECK (hours >= 0),
    status VARCHAR(50) CHECK (status IN ('pending', 'approved', 'rejected')) DEFAULT 'pending',

    CONSTRAINT fk_overtime_user
        FOREIGN KEY (emp_id)
        REFERENCES users(emp_id)
);
-- rate is constant

INSERT INTO overtime (emp_id, date, hours, status)
VALUES
(3, '2024-06-10', 3.5, 'approved');




