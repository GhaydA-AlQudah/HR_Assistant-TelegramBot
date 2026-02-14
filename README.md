# 🤖 HR Assistant - TelegramBot

## Problem Statement

Traditionally, HR processes are synonymous with **Waiting**. Employees often find themselves caught in a loop of sending emails, checking portal statuses, or manually tracking their leave balances on spreadsheets.

## System Architecture


```
┌──────────────────────────────┐
│       Interface Layer        │
│  Telegram Bot API (UI Entry) │
└───────────────┬──────────────┘
                ↓
┌──────────────────────────────┐
│      Agentic Layer           │
│  Pydantic AI Agent ("Brain") │
│    • Tool Calling            │
└───────────────┬──────────────┘
                ↓
┌───────────────────────────────────┐
│        Service Layer              │
│  Business Logic Encapsulation     │
│  • Onboarding                     │
│  • Leave Request                  │
│  • Authentication                 |
|  • Leaves Balance                 |
|  • My Info                        |
|  • Other Employees Info           |
|     - Role-based                  |        
└───────────────┬───────────────────┘
                ↓
┌──────────────────────────────────┐
│         Domain Models            │
│  OOP-Based HR Entities           │
│  • Employees                     │
│  • Managers                      │
│  • Leaves                        │
└───────────────┬──────────────────┘
                ↓
┌──────────────────────────────────┐
│         Data Access Layer        │
│  PostgreSQL (Snowflake Schema)   │
│  • ACID Transactions             │
│  • Relational Integrity          │
└──────────────────────────────────┘
```
- The project adopts **a Modular Monolith architecture** with a clear **Separation of Concerns**, ensuring high maintainability and seamless scalability.

- Secure Authentication & Authorization: Access is strictly limited to registered Telegram IDs. The system dynamically detects **the user's id** and enforces **Role-Based Privileges** to gatekeep all database interactions, preventing unauthorized access or data manipulation.

- The LLM acts as a **Conversational Orchestrator**: for intent detection and parameter extraction, triggering tools without "inventing" data.

- Service-Layer **(Business Logic Encapsulation)**: All business rules—such as leave balance validation and onboarding are encapsulated within the Service Layer to ensure a clean separation from data models.

- **Single Source of Truth**: All information originates from a deterministic PostgreSQL database, 
   following a strict **Telegram > LLM > Tool > Service > DB flow**.


## Database Schema

![Database Schema](github_assets/DB%20Schema.png)


## Features

### Global (Manager, Employee, HR)

**Leave Request:** Simplified process to request time off using natural language, which automatically checks balance and dates before submission.

**Role-Based Data Access:** The system enforces strict permission layers; managers can query private employee records within their scope,                      whereas general staff access is limited to a public directory (Name, Role, and Contact info)."
**My Info:** read-only view info.

**Leaves Balance PDF:** Generation of professional HR reports as PDF.

### HR
**Onboarding:** HR staff can add new employees via natural language commands.



---

## Technologies Used
Language: Python 3.10+

**Pydantic AI Framework:**  (Strict Schema Validation & Guardrails)
- less tokens , tool calling, scalable
- pydantic ai cost tokens agentic

why pydantic ai?

- ux - 1 or 2 at once services
- cost - smaller prompt Tokens
- scalability - adding
 more service without need to a new prompt 


**LLM Provider:** OpenRouter (google/gemma-3-27b-it:free)

**Database:** PostgreSQL (Relational Modeling - Snowflake)
why postgresql

**Bot Framework:** python-telegram-bot (Asynchronous handling)

**Dotenv** (Environment Management)


##  Installation

### Clone the repository:

```
git clone https://github.com/GhaydA-AlQudah/HR_Assistant-TelegramBot.git
cd HR_Assistant-TelegramBot
```

### Setup Environment Variables: Create a .env file in the root directory:

PYDANTIC_AI_GATEWAY_API_KEY=YOUR PYDANTIC_AI_GATEWAY_API_KEY
OPENROUTER_API_KEY=YOUR OPENROUTER_API_KEY
TELEGRAM_BOT_TOKEN=your_token_here
DB_HOST=localhost
DB_NAME=HR_ChatBot
DB_USER=postgres
DB_PASS=your_password
DB_PORT=5432


### Install Dependencies:

```
pip install -r requirements.txt
```
### Initialize Database: 
Run your SQL migration scripts in PostgreSQL to set up the tables.

### Run the Bot:

```
python TelegramBot.py
```

## Examples 
### Global Services(Manager/ Employee/ HR)

#### Manager/ Employee Menu


![Manager/ Employee Menu](github_assets/logged%20as%20Manager%20-%20GhaydA.png)


#### Info Service

![Manager/ Employee/ HR Info](github_assets/my%20info.png)


#### Leave Request Service
![Manager/ Employee/ HR Leave Request](github_assets/leave_request.png)


#### Leave Balance Service 
![Manager/ Employee/ HR Leave Balance](github_assets/leaves_balance_request_Jameelah.png)


#### Leave Balance PDF

![Manager/ Employee/ HR Leave Balance PDF](github_assets/leaves%20balance.png)


#### Other Employees Info Service - Different Privelages 

![Manager/ Employee/ HR Employees Info](github_assets/employees%20info%20.png)


#### What if Manager or Employee attepts to onboard a new employee

![attempt to onboard a new employee](github_assets/denied_onboarding.png)



### Services Resticted for HR - HR Menue

#### HR Menu

![HR Menu](github_assets/HR%20Menu.png)


#### Onboarding Service                                  
![Onboarding](github_assets/onboarding.png)             


#### Onboarding-DB-users-table
![Onboarding-DB-users-table](github_assets/onboarding-db.png)


### Request for a Service By Messages

![Request By Messeges](github_assets/request_by_messages.png)


### Other Services

![Other Services](github_assets/payroll_under_maintanance.png)

### Mitigating Prompt Leakage via an Input Sanitization Layer - Defending Against Prompt Injection

#### before adding Input Sanitization Layer

![non_secure_system_prompt](github_assets/non_secured.png)

#### ِAfter 
![Secure_system_prompt](github_assets/secured_system_prompt.png)


## Business Limitations
1. **Service Availability & Resilience:** The system's uptime is intrinsically linked to **third-party** API providers (OpenRouter & Telegram).
2. **Data Sovereignty & Compliance:** Processing sensitive HR data via public LLM endpoints requires careful alignment with **GDPR**.
3. Token Consumption & Scalability Costs.


## Future Work
- [ ] **Advanced Fallbacks:**  for Unexpected Inputs & Edge Cases.
- [ ] **Service Expansion:** Modularizing Payroll and Performance Review services.
- [ ] **Usage Governance:** Enforcing API **rate-limiting** and per-user request quotas.
- [ ] **Multi-Channel Support:** Bringing the HR Agent to Slack and MS Teams.
- [ ] Implementation of strict **rate-limiting (Hard Cap)** to optimize LLM token consumption.
- [ ] Decoupling services into independent  **Microservices ecosystem**.


## 👤 Author

**By GhaydA' Al-Qudah**

**Computer Engineer | AI Enthusiast**
