# Gharpayy Lead Management CRM - MVP

A rapid prototype Minimum Viable Product built for the Gharpayy 48-hour assignment.

## Tech Stack
* **Frontend:** Python / Streamlit (styled with custom light-theme configurations and Plotly)
* **Backend logic:** Python / Pandas
* **Database:** SQLite3

## Note on Architecture & Scalability
For the sake of rapid prototyping within the 48-hour window, this MVP uses a local SQLite database. Because it is deployed on Streamlit Community Cloud's ephemeral file system, local data will reset upon container restart. 

For the production evolution of this product, the database layer would be migrated to a managed PostgreSQL instance (e.g., Supabase, AWS RDS) to ensure persistent storage, handle concurrent users, and implement row-level security for different agent roles.

---

## 🚀 Future Product Evolution (Arena Architecture Alignment)
While this 48-hour MVP successfully handles core lead state-tracking and agent assignment, the architecture is designed to scale into a high-speed, two-sided operational layer. Future iterations would integrate:

*   **Dynamic Inventory Matching (Supply Hub):** Transitioning from general "PG Location" interest to binding scheduled visits to specific, real-time `Room IDs` using a live inventory matrix.
*   **SLA Automations & Action Queues:** Upgrading the pipeline from a passive Kanban board to an active "Inbox Zero" queue (e.g., flagging leads if Flow Ops hasn't actioned them within a 2-hour window, or auto-pausing sequences on replies).
*   **Closed-Loop TCM Reporting:** Expanding the "Visit Scheduled" phase to mandate a 15-minute post-tour update form. This captures granular objection data, feeding insights directly back to property owners to prevent stale supply.
*   **Automated Sequences:** Implementing background workers to handle pre-decision and cold-revival follow-ups automatically, allowing the TCM team to focus exclusively on hot, ranked leads.
