# Sales Dashboard

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/AdagamovNikita/Dashboard.git
   cd Dashboard
   ```

2. **Set Up Python Environment**
   - Python 3.x required
   - Create virtual environment:
   ```bash
   python -m venv venv
   ```
   - Activate virtual environment:
     - Windows:
     ```bash
     venv\Scripts\activate
     ```
     - Unix/MacOS:
     ```bash
     source venv/bin/activate
     ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Database**
   ```bash
   python init_db.py
   ```
   This will create store.db with sample data including:
   - Products across categories
   - 30 days of sales data
   - Product attributes and pricing
   - Supplier information
   - Promo codes

5. **Run Application**
   ```bash
   python app.py
   ```

6. **Access Dashboard**
   - Open web browser
   - Navigate to http://127.0.0.1:5000

## Features
- Real-time sales visualization
- Product category analysis
- Interactive ECharts graphs
- Sales trend analysis
- Product inventory tracking

## Troubleshooting
If you encounter issues:
1. Delete store.db file
2. Run init_db.py again
3. Restart application
