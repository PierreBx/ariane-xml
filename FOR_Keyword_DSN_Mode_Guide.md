# The FOR Keyword in DSN Mode

## What is DSN Mode?

**DSN (Déclaration Sociale Nominative)** is a French social declaration XML format used for reporting payroll and employee data. Ariane-XML provides special DSN mode to make querying these complex XML files much easier.

### Three Types of DSN Files:

1. **Mensuelle** - Monthly declarations (salaries, contributions, payments)
2. **FCTU** - Fin de Contrat de Travail Unique (employment termination)
3. **SADV** - Arrêt de travail (sick leave notifications)

**This guide focuses on Mensuelle files** - the most commonly used type for monthly payroll declarations.

---

## How DSN Mode Works with FOR

The **FOR keyword syntax remains identical** in DSN mode, but DSN mode provides **shortcut notation** that makes queries much cleaner.

### Standard Mode vs DSN Mode

**Standard Mode (verbose):**
```sql
SELECT S21_G00_30_002, S21_G00_30_006
FROM "data.xml"
FOR e IN S21_G00_30
WHERE S21_G00_30_002 IS NOT NULL;
```

**DSN Mode (clean):**
```sql
SET MODE DSN;
SELECT 30.002, 30.006
FROM "data.xml"
FOR e IN 30
WHERE 30.002 IS NOT NULL;
```

**Same query, much easier to read!**

---

## The YY.ZZZ Shortcut Notation

DSN mode uses a special **YY.ZZZ pattern**:

- **YY** = 2-digit bloc identifier (e.g., `30` = INDIVIDU/employee, `40` = CONTRAT/contract)
- **ZZZ** = 3-digit field identifier within the bloc (e.g., `001`, `002`)

### Common DSN Blocs:

| Code | Name | Description |
|------|------|-------------|
| `10` | ENVOI | Envelope/transmission metadata |
| `20` | DSN MENSUELLE | Root of monthly declaration |
| `21` | ENTREPRISE | Company information |
| `30` | INDIVIDU | Employee/individual |
| `40` | CONTRAT | Employment contract |
| `50` | VERSEMENT | Individual payment |
| `51` | RÉMUNÉRATION | Remuneration details |
| `78` | BASE ASSUJETTIE | Contribution base |

### Activation:

```sql
SET MODE DSN;           -- Enable DSN mode
SET DSN_VERSION P26;    -- Specify version (P25 or P26)
```

---

## Mensuelle File Structure

A typical **Mensuelle XML file** has this hierarchy:

```
S10.G00.00   ENVOI (envelope)
  └─ S20.G00.05   DSN MENSUELLE
      └─ S21.G00.06   ENTREPRISE (company)
          └─ S21.G00.11   ETABLISSEMENT (establishment)
              └─ S21.G00.30   INDIVIDU (employee) [0..many]
                  ├─ S21.G00.40   CONTRAT (contract) [1..many]
                  │   └─ S21.G00.62   FIN DE CONTRAT (end) [0..1]
                  └─ S21.G00.50   VERSEMENT (payment) [1..many]
                      ├─ S21.G00.51   RÉMUNÉRATION [0..many]
                      └─ S21.G00.78   BASE ASSUJETTIE [0..many]
```

**Key Point:** One employee (INDIVIDU) can have:
- **Multiple contracts** (CONTRAT)
- **Multiple payments** (VERSEMENT)
- Each payment can have **multiple remuneration items** (RÉMUNÉRATION)

This is **exactly the scenario FOR was designed for!**

---

## Example 1: Basic Employee Iteration

### XML Structure (simplified):

```xml
<S20_G00_05>
  <S21_G00_30>
    <S21_G00_30_001>1</S21_G00_30_001>  <!-- Employee ID -->
    <S21_G00_30_002>Alice Martin</S21_G00_30_002>  <!-- Name -->
    <S21_G00_30_006>1985-03-15</S21_G00_30_006>  <!-- Birth date -->
  </S21_G00_30>
  <S21_G00_30>
    <S21_G00_30_001>2</S21_G00_30_001>
    <S21_G00_30_002>Bob Dupont</S21_G00_30_002>
    <S21_G00_30_006>1990-07-22</S21_G00_30_006>
  </S21_G00_30>
</S20_G00_05>
```

### Query:

```sql
SET MODE DSN;
SET DSN_VERSION P26;

SELECT e.30.001 AS id, e.30.002 AS name, e.30.006 AS birth_date
FROM "./mensuelle_janvier_2025.xml"
FOR e IN 30;
```

### Result:

```
id | name          | birth_date
---+---------------+------------
1  | Alice Martin  | 1985-03-15
2  | Bob Dupont    | 1990-07-22
```

### What Happens:

- `FOR e IN 30` - Iterate over each INDIVIDU (employee) bloc
- `e.30.001` - Within variable `e`, get field 001 (employee ID)
- `e.30.002` - Within variable `e`, get field 002 (name)
- DSN mode automatically converts `30` → `S21_G00_30`

---

## Example 2: Nested Iteration - Employees and Contracts

### XML Structure:

```xml
<S21_G00_30>
  <S21_G00_30_002>Alice Martin</S21_G00_30_002>
  <S21_G00_40>
    <S21_G00_40_001>2020-01-15</S21_G00_40_001>  <!-- Contract start -->
    <S21_G00_40_007>CDI</S21_G00_40_007>         <!-- Contract type -->
  </S21_G00_40>
  <S21_G00_40>
    <S21_G00_40_001>2018-06-01</S21_G00_40_001>
    <S21_G00_40_007>CDD</S21_G00_40_007>
  </S21_G00_40>
</S21_G00_30>
<S21_G00_30>
  <S21_G00_30_002>Bob Dupont</S21_G00_30_002>
  <S21_G00_40>
    <S21_G00_40_001>2019-03-10</S21_G00_40_001>
    <S21_G00_40_007>CDI</S21_G00_40_007>
  </S21_G00_40>
</S21_G00_30>
```

### Query:

```sql
SET MODE DSN;

SELECT e.30.002 AS employee, c.40.001 AS start_date, c.40.007 AS type
FROM "./mensuelle_janvier_2025.xml"
FOR e IN 30
FOR c IN e/40;
```

### Result:

```
employee      | start_date | type
--------------+------------+------
Alice Martin  | 2020-01-15 | CDI
Alice Martin  | 2018-06-01 | CDD
Bob Dupont    | 2019-03-10 | CDI
```

### What Happens:

- **First FOR** (`FOR e IN 30`) - Loop through employees
- **Second FOR** (`FOR c IN e/40`) - For each employee, loop through their contracts
- **Notice:** `e/40` means "find bloc 40 (CONTRAT) within variable `e`"
- **Result:** One row per employee-contract combination (cartesian product)

---

## Example 3: Three-Level Iteration - Employees, Contracts, Payments

### Query:

```sql
SET MODE DSN;

SELECT
    e.30.002 AS employee,
    c.40.007 AS contract_type,
    v.50.001 AS payment_date,
    r.51.001 AS amount
FROM "./mensuelle_janvier_2025.xml"
FOR e IN 30          -- Employees
FOR c IN e/40       -- Contracts within each employee
FOR v IN e/50       -- Payments within each employee
FOR r IN v/51;      -- Remuneration within each payment
```

### Result:

```
employee      | contract_type | payment_date | amount
--------------+---------------+--------------+---------
Alice Martin  | CDI           | 2025-01-31   | 3500.00
Alice Martin  | CDI           | 2025-01-31   | 150.00
Alice Martin  | CDD           | 2025-01-31   | 3500.00
Alice Martin  | CDD           | 2025-01-31   | 150.00
Bob Dupont    | CDI           | 2025-01-31   | 4200.00
```

### What Happens:

- **Four nested FOR clauses** create a cartesian product
- Each employee can have multiple contracts
- Each employee can have multiple payments
- Each payment can have multiple remuneration items
- **Result:** All combinations are shown

---

## Example 4: Filtering with WHERE

### Query - Only CDI (Permanent) Contracts:

```sql
SET MODE DSN;

SELECT e.30.002 AS employee, c.40.001 AS start_date
FROM "./mensuelle_janvier_2025.xml"
FOR e IN 30
FOR c IN e/40
WHERE c.40.007 = 'CDI';
```

### Result:

```
employee      | start_date
--------------+------------
Alice Martin  | 2020-01-15
Bob Dupont    | 2019-03-10
```

### Query - Salaries Above Threshold:

```sql
SET MODE DSN;

SELECT e.30.002 AS employee, r.51.001 AS salary
FROM "./mensuelle_janvier_2025.xml"
FOR e IN 30
FOR v IN e/50
FOR r IN v/51
WHERE r.51.001 > 3000;
```

**Notice:** Variables from FOR clauses (`e`, `c`, `r`) are used in WHERE conditions!

---

## Example 5: Aggregation - Count Contracts per Employee

### Query:

```sql
SET MODE DSN;

SELECT e.30.002 AS employee, COUNT(c) AS contract_count
FROM "./mensuelle_janvier_2025.xml"
FOR e IN 30
FOR c IN e/40
GROUP BY e.30.002;
```

### Result:

```
employee      | contract_count
--------------+----------------
Alice Martin  | 2
Bob Dupont    | 1
```

### What Happens:

- `COUNT(c)` counts how many contracts each employee has
- `GROUP BY e.30.002` groups results by employee name
- FOR provides the context needed for proper grouping

---

## Example 6: Finding Employees with Multiple Contracts

### Query:

```sql
SET MODE DSN;

SELECT e.30.002 AS employee, COUNT(c) AS contract_count
FROM "./mensuelle_janvier_2025.xml"
FOR e IN 30
FOR c IN e/40
GROUP BY e.30.002
HAVING COUNT(c) > 1;
```

### Result:

```
employee      | contract_count
--------------+----------------
Alice Martin  | 2
```

**Only employees with more than one contract are shown.**

---

## Example 7: Position Tracking with AT

### Query:

```sql
SET MODE DSN;

SELECT pos, e.30.002 AS employee
FROM "./mensuelle_janvier_2025.xml"
FOR e IN 30 AT pos
LIMIT 5;
```

### Result:

```
pos | employee
----+--------------
1   | Alice Martin
2   | Bob Dupont
3   | Carol Leblanc
4   | David Rousseau
5   | Emma Bernard
```

**Useful for numbering employees or selecting specific positions.**

---

## Real-World Use Cases

### Use Case 1: Monthly Payroll Report

```sql
SET MODE DSN;

SELECT
    e.30.001 AS matricule,
    e.30.002 AS nom,
    v.50.001 AS date_versement,
    SUM(r.51.001) AS total_brut
FROM "./mensuelle_janvier_2025.xml"
FOR e IN 30
FOR v IN e/50
FOR r IN v/51
GROUP BY e.30.001, e.30.002, v.50.001
ORDER BY e.30.002;
```

**Purpose:** Calculate total gross salary per employee for the month.

---

### Use Case 2: Find Terminated Contracts

```sql
SET MODE DSN;

SELECT
    e.30.002 AS employee,
    c.40.001 AS contract_start,
    fc.62.001 AS termination_date,
    fc.62.002 AS termination_reason
FROM "./mensuelle_janvier_2025.xml"
FOR e IN 30
FOR c IN e/40
FOR fc IN c/62
WHERE fc.62.001 IS NOT NULL;
```

**Purpose:** List all employees whose contracts ended this month.

---

### Use Case 3: Contribution Base Analysis

```sql
SET MODE DSN;

SELECT
    e.30.002 AS employee,
    ba.78.001 AS contribution_type,
    ba.78.002 AS base_amount
FROM "./mensuelle_janvier_2025.xml"
FOR e IN 30
FOR v IN e/50
FOR ba IN v/78
WHERE ba.78.001 = '02'  -- Social security base
ORDER BY ba.78.002 DESC
LIMIT 10;
```

**Purpose:** Analyze contribution bases for social security calculations.

---

## Key Concepts in DSN Mode

### 1. Variable Scoping

Variables from outer FOR clauses are **accessible in inner FOR clauses**:

```sql
FOR e IN 30          -- 'e' available everywhere below
FOR c IN e/40       -- 'c' references 'e' from outer FOR
FOR v IN e/50       -- 'v' also references 'e'
```

### 2. Cartesian Product

Multiple FOR clauses create **all combinations**:

- 2 employees × 3 contracts each = 6 rows
- Then × 4 payments each = 24 rows
- Then × 2 remuneration items each = 48 rows

### 3. Partial Path Search

DSN shortcuts (like `30`, `40.007`) are automatically marked as **partial paths**, enabling recursive XML element search throughout the document.

### 4. Pseudonymisation Support

In DSN mode, only files marked with `<?pseudonymised?>` processing instruction are included in results (for GDPR compliance).

---

## Common Mensuelle Field Reference

### INDIVIDU (30) - Employee Fields:

| Code | Field | Description |
|------|-------|-------------|
| 30.001 | Identifiant | Employee ID/matricule |
| 30.002 | Nom famille | Last name |
| 30.003 | Prénoms | First names |
| 30.006 | Date naissance | Birth date |
| 30.007 | Lieu naissance | Birth place |

### CONTRAT (40) - Contract Fields:

| Code | Field | Description |
|------|-------|-------------|
| 40.001 | Date début | Contract start date |
| 40.007 | Nature | Contract type (CDI, CDD, etc.) |
| 40.008 | Dispositif | Contract scheme |
| 40.009 | Statut conventionnel | Convention status |

### VERSEMENT (50) - Payment Fields:

| Code | Field | Description |
|------|-------|-------------|
| 50.001 | Date versement | Payment date |
| 50.002 | Montant | Payment amount |

### RÉMUNÉRATION (51) - Remuneration Fields:

| Code | Field | Description |
|------|-------|-------------|
| 51.001 | Montant | Amount |
| 51.002 | Type | Remuneration type |

---

## DSN Mode Commands Summary

```sql
-- Activate DSN mode
SET MODE DSN;

-- Set version
SET DSN_VERSION P25;     -- For older P25 files
SET DSN_VERSION P26;     -- For current P26 files
SET DSN_VERSION AUTO;    -- Auto-detect from XML

-- Check current state
SHOW MODE;               -- Display current mode
SHOW DSN_SCHEMA;         -- Show loaded schema

-- Describe fields
DESCRIBE 30;             -- Show all INDIVIDU fields
DESCRIBE 30.002;         -- Show specific field details

-- Return to standard mode
SET MODE STANDARD;
```

---

## Tips for Using FOR in DSN Mode

✅ **DO:**
- Use YY.ZZZ notation (`30.002` not `S21_G00_30_002`)
- Reference outer variables in inner FOR clauses (`e/40`)
- Use meaningful variable names (`e` for employee, `c` for contract)
- Filter with WHERE to reduce result size

❌ **DON'T:**
- Use leading dots (`.30.002` is forbidden in DSN mode)
- Mix full names with shortcuts in DSN mode
- Forget to SET MODE DSN first
- Omit the .ZZZ part (must be `30.001`, not just `30`)

---

## Complete Example: Monthly Analysis

```sql
-- Activate DSN mode
SET MODE DSN;
SET DSN_VERSION P26;

-- Comprehensive monthly report
SELECT
    e.30.001 AS matricule,
    e.30.002 AS employee_name,
    c.40.007 AS contract_type,
    COUNT(DISTINCT v.50.001) AS payment_count,
    SUM(r.51.001) AS total_gross_salary,
    AVG(r.51.001) AS avg_remuneration
FROM "./mensuelle_janvier_2025.xml"
FOR e IN 30              -- Loop through employees
FOR c IN e/40           -- Loop through their contracts
FOR v IN e/50           -- Loop through their payments
FOR r IN v/51           -- Loop through remuneration items
WHERE c.40.007 = 'CDI'  -- Only permanent contracts
GROUP BY
    e.30.001,
    e.30.002,
    c.40.007
HAVING SUM(r.51.001) > 3000  -- Total above 3000€
ORDER BY total_gross_salary DESC
LIMIT 100;
```

**This query demonstrates:**
- Multiple nested FOR clauses
- Filtering with WHERE
- Aggregation with GROUP BY
- Post-aggregation filtering with HAVING
- All using clean DSN shortcut notation!

---

## Summary

The **FOR keyword in DSN mode** is **essential for querying Mensuelle files** because:

1. **Mensuelle files are deeply hierarchical** - Employees → Contracts → Payments → Remuneration
2. **YY.ZZZ shortcuts make queries readable** - `30.002` instead of `S21_G00_30_002`
3. **Nested FOR clauses handle one-to-many relationships** - One employee can have multiple contracts and payments
4. **Variables enable cross-referencing** - Use `e/40` to find contracts within employee `e`
5. **Real-world payroll analysis requires iteration** - Calculate totals, averages, counts across hierarchies

**Think of FOR in DSN mode as the bridge between complex French social declaration XML structures and simple, SQL-like queries.**
