# FinKG-news

This repository contains all the code used for the FinKG-news project, covering from the event detection task in news article text, to the Knowledge Graph generation in neo4j and its application in the financial report generation use case.

---

## Repository Structure
The repository is organized into three main modules:

- **event_detection/**  
  Code and resources for working with the news dataset, preprocessing events, and running event detection on news articles.
- **kg_generation/**  
  Code and utilities for generating the Knowledge Graph in Neo4j from detected events and resources from SEC.
- **report_generation/**  
  Code and scripts for the use case we selected: generating financial reports using the Knowledge Graph and other external resources.

---

## Getting Started

1. **Clone the repository**
```bash
   git clone <your-repo-url>  
   cd FinKG-news
```
2. **Set up environments**  
   Since each module is designed to run independently I recommend to:
   - Create a separate **virtual environment** for each folder (`event_detection`, `kg_generation`, `report_generation`).
   - Add a `.env` file with the required environment variables, for example:

```
     OPENAI_API_KEY=your_api_key_here  
     NEO_USERNAME=your_username  
     NEO_PASSWORD=your_password  
```

3. **Follow instructions in each folder**  
   Each subfolder contains its own README with setup and usage instructions.
