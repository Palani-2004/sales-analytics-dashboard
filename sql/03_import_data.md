# Import clean_sales_data.csv into sales_raw

1. Open MySQL Workbench.

2. Expand:

sales_analytics_db

↓

Tables

↓

sales_raw

3. Right-click **sales_raw**

4. Select **Table Data Import Wizard**

5. Browse to:

data/cleaned/clean_sales_data.csv

6. Click Next

7. Verify all column mappings.

8. Click Next

9. Click Finish

After importing, verify:

```sql
SELECT COUNT(*) FROM sales_raw;
```