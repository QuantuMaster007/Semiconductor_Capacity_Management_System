# 🚀 Setup Guide

## Quick Setup (5 Minutes)

### Step 1: Install Python
Ensure you have Python 3.9 or higher:
```bash
python --version
```

### Step 2: Clone Repository
```bash
git clone <your-repo-url>
cd semiconductor-capacity-system
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run System
```bash
python main.py --full
```

### Step 5: Access Dashboard
Open browser to: `http://localhost:8050`

---

## Detailed Setup

### Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Verify Installation

```bash
# Test data generation
python main.py --generate

# Test analytics
python main.py --analyze

# Test report
python main.py --report
```

---

## Usage Modes

### Interactive Menu
```bash
python main.py --menu
```

### Full Pipeline
```bash
python main.py --full
```

### Individual Components
```bash
# Generate data only
python main.py --generate

# Run analytics only
python main.py --analyze

# Launch dashboard only
python main.py --dashboard

# Generate report only
python main.py --report
```

---

## Docker Deployment

### Build Image
```bash
docker build -t capacity-management .
```

### Run Container
```bash
docker run -p 8050:8050 capacity-management
```

---

## Troubleshooting

### Issue: ModuleNotFoundError
**Solution:** Install missing package
```bash
pip install <package-name>
```

### Issue: Port 8050 already in use
**Solution:** Change port in dashboard code or kill existing process
```bash
# Find process using port 8050
lsof -i :8050

# Kill process
kill -9 <PID>
```

### Issue: Data files not found
**Solution:** Run data generation first
```bash
python main.py --generate
```

---

## System Requirements

- **Python:** 3.9 or higher
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 500MB for code + data
- **Browser:** Chrome, Firefox, Safari, or Edge (latest versions)

---

## Performance Tips

1. **Data Generation:** Initial generation takes 2-3 minutes
2. **Analytics:** Monte Carlo simulation (10K iterations) takes 30-60 seconds
3. **Dashboard:** First load takes 15-20 seconds, subsequent loads are instant

---

## Need Help?

- Check README.md for detailed documentation
- Review code comments for technical details
- Contact: [sourabh232@gmail.com]
