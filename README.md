# Bincom ICT Assessment - Django Project

## 1. Import the database
```bash
mysql -u root -p -e "CREATE DATABASE bincom_test CHARACTER SET utf8mb4;"
mysql -u root -p bincom_test < bincom_test.sql
```

## 2. Install and configure
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Set your MySQL password either by editing `bincom_project/settings.py`
or with environment variables:

```bash
export DB_NAME=bincom_test
export DB_USER=root
export DB_PASSWORD=your_mysql_password
export DB_HOST=127.0.0.1
export DB_PORT=3306
```
(Windows PowerShell: `$env:DB_PASSWORD="your_mysql_password"`)

If `mysqlclient` fails to install, run `pip install pymysql` and put these
two lines at the top of `bincom_project/__init__.py`:
```python
import pymysql
pymysql.install_as_MySQLdb()
```

## 3. Run
```bash
python manage.py migrate        # creates Django's own tables only
python manage.py runserver
```
Do NOT run `makemigrations` for `election`: the models are `managed = False`
and map onto the tables that already exist in the imported dump.

## 4. Pages
- http://127.0.0.1:8000/                    Question 1: polling unit results
- http://127.0.0.1:8000/lga-results/        Question 2: summed LGA results
- http://127.0.0.1:8000/add-polling-unit/   Question 3: add polling unit

## Verify the models against your dump
```bash
python manage.py inspectdb lga polling_unit announced_pu_results
```
