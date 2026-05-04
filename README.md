# Gharpayy Lead Management CRM - MVP

A rapid prototype Minimum Viable Product built for the Gharpayy 48-hour assignment.

## Tech Stack
* **Frontend:** Python / Streamlit (styled with custom light-theme configurations and Plotly)
* **Backend logic:** Python / Pandas
* **Database:** SQLite3

## Note on Architecture & Scalability
For the sake of rapid prototyping within the 48-hour window, this MVP uses a local SQLite database. Because it is deployed on Streamlit Community Cloud's ephemeral file system, local data will reset upon container restart. 

For the production evolution of this product, the database layer would be migrated to a managed PostgreSQL instance (e.g., Supabase, AWS RDS) to ensure persistent storage, handle concurrent users, and implement row-level security for different agent roles.
