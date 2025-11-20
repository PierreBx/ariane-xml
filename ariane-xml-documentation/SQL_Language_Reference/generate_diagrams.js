#!/usr/bin/env node

/**
 * Railroad Diagram Generator for Ariane-XML SQL Grammar
 *
 * This script generates SVG railroad diagrams for the SQL grammar.
 * Based on the EBNF grammar defined in ebnf/ariane-xml-sql-grammar.ebnf
 */

const fs = require('fs');
const path = require('path');
const Diagram = require('railroad-diagrams');

// Output directory
const OUTPUT_DIR = path.join(__dirname, 'diagrams');

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

// Helper functions
const T = (text) => Diagram.Terminal(text);
const NT = (text) => Diagram.NonTerminal(text);
const Opt = (...args) => Diagram.Optional(...args);
const Choice = (defaultIdx, ...args) => Diagram.Choice(defaultIdx, ...args);
const OneOrMore = (...args) => Diagram.OneOrMore(...args);
const ZeroOrMore = (...args) => Diagram.ZeroOrMore(...args);
const Seq = (...args) => Diagram.Sequence(...args);

/**
 * Save diagram to SVG file
 */
function saveDiagram(diagram, filename) {
  const svg = diagram.toString();
  const filepath = path.join(OUTPUT_DIR, filename);
  fs.writeFileSync(filepath, svg);
  console.log(`Generated: ${filename}`);
}

/* ====================
   1. SELECT Statement (Main)
   ==================== */

const selectStatement = Diagram.Diagram(
  Seq(
    T('SELECT'),
    Opt(T('DISTINCT')),
    NT('field_list'),
    NT('from_clause'),
    ZeroOrMore(NT('for_clause')),
    Opt(NT('where_clause')),
    Opt(NT('group_by_clause')),
    Opt(NT('having_clause')),
    Opt(NT('order_by_clause')),
    Opt(NT('limit_clause')),
    Opt(NT('offset_clause'))
  )
);

saveDiagram(selectStatement, 'select_statement.svg');

/* ====================
   2. Field List
   ==================== */

const fieldList = Diagram.Diagram(
  OneOrMore(NT('field'), T(','))
);

saveDiagram(fieldList, 'field_list.svg');

/* ====================
   3. Field
   ==================== */

const field = Diagram.Diagram(
  Choice(
    0,
    NT('aggregation_function'),
    T('FILE_NAME'),
    Seq(
      NT('field_path_expression'),
      Opt(Seq(T('AS'), NT('identifier')))
    )
  )
);

saveDiagram(field, 'field.svg');

/* ====================
   4. Aggregation Function
   ==================== */

const aggregationFunction = Diagram.Diagram(
  Seq(
    Choice(0, T('COUNT'), T('SUM'), T('AVG'), T('MIN'), T('MAX')),
    T('('),
    NT('field_path_expression'),
    T(')'),
    Opt(Seq(T('AS'), NT('identifier')))
  )
);

saveDiagram(aggregationFunction, 'aggregation_function.svg');

/* ====================
   5. Field Path Expression
   ==================== */

const fieldPathExpression = Diagram.Diagram(
  Choice(
    0,
    // Partial path: .field.subfield
    Seq(
      T('.'),
      NT('identifier'),
      ZeroOrMore(Seq(Choice(0, T('.'), T('/')), NT('identifier')))
    ),
    // Absolute path: field.subfield
    Seq(
      NT('identifier'),
      ZeroOrMore(Seq(Choice(0, T('.'), T('/')), NT('identifier')))
    ),
    // Attribute: @attribute
    Seq(T('@'), NT('identifier')),
    // Variable reference: var.field
    Seq(
      NT('variable'),
      Opt(Seq(T('.'), NT('identifier')))
    )
  )
);

saveDiagram(fieldPathExpression, 'field_path_expression.svg');

/* ====================
   6. FROM Clause
   ==================== */

const fromClause = Diagram.Diagram(
  Seq(
    T('FROM'),
    NT('file_path')
  )
);

saveDiagram(fromClause, 'from_clause.svg');

/* ====================
   7. FOR Clause (ariane-xml specific)
   ==================== */

const forClause = Diagram.Diagram(
  Seq(
    T('FOR'),
    NT('identifier'),
    T('IN'),
    NT('field_path_expression'),
    Opt(Seq(T('AT'), NT('identifier')))
  )
);

saveDiagram(forClause, 'for_clause.svg');

/* ====================
   8. WHERE Clause
   ==================== */

const whereClause = Diagram.Diagram(
  Seq(
    T('WHERE'),
    NT('where_expression')
  )
);

saveDiagram(whereClause, 'where_clause.svg');

/* ====================
   9. WHERE Expression (OR level)
   ==================== */

const whereOrExpression = Diagram.Diagram(
  Seq(
    NT('where_and_expression'),
    ZeroOrMore(
      Seq(T('OR'), NT('where_and_expression'))
    )
  )
);

saveDiagram(whereOrExpression, 'where_or_expression.svg');

/* ====================
   10. WHERE Expression (AND level)
   ==================== */

const whereAndExpression = Diagram.Diagram(
  Seq(
    NT('where_primary'),
    ZeroOrMore(
      Seq(T('AND'), NT('where_primary'))
    )
  )
);

saveDiagram(whereAndExpression, 'where_and_expression.svg');

/* ====================
   11. WHERE Primary
   ==================== */

const wherePrimary = Diagram.Diagram(
  Choice(
    0,
    Seq(T('('), NT('where_expression'), T(')')),
    NT('condition')
  )
);

saveDiagram(wherePrimary, 'where_primary.svg');

/* ====================
   12. Condition
   ==================== */

const condition = Diagram.Diagram(
  Choice(
    0,
    // Comparison: field = value
    Seq(
      NT('field_path_expression'),
      Choice(0, T('='), T('!='), T('<'), T('>'), T('<='), T('>=')),
      NT('value')
    ),
    // NULL check: field IS [NOT] NULL
    Seq(
      NT('field_path_expression'),
      T('IS'),
      Opt(T('NOT')),
      T('NULL')
    ),
    // LIKE: field [NOT] LIKE /regex/
    Seq(
      NT('field_path_expression'),
      Opt(T('NOT')),
      T('LIKE'),
      NT('regex_pattern')
    ),
    // IN: field [NOT] IN (values)
    Seq(
      NT('field_path_expression'),
      Opt(T('NOT')),
      T('IN'),
      T('('),
      NT('value_list'),
      T(')')
    )
  )
);

saveDiagram(condition, 'condition.svg');

/* ====================
   13. GROUP BY Clause
   ==================== */

const groupByClause = Diagram.Diagram(
  Seq(
    T('GROUP'),
    T('BY'),
    OneOrMore(NT('field_name'), T(','))
  )
);

saveDiagram(groupByClause, 'group_by_clause.svg');

/* ====================
   14. HAVING Clause
   ==================== */

const havingClause = Diagram.Diagram(
  Seq(
    T('HAVING'),
    NT('where_expression')
  )
);

saveDiagram(havingClause, 'having_clause.svg');

/* ====================
   15. ORDER BY Clause
   ==================== */

const orderByClause = Diagram.Diagram(
  Seq(
    T('ORDER'),
    T('BY'),
    OneOrMore(
      Seq(
        NT('field_name'),
        Opt(Choice(0, T('ASC'), T('DESC')))
      ),
      T(',')
    )
  )
);

saveDiagram(orderByClause, 'order_by_clause.svg');

/* ====================
   16. LIMIT Clause
   ==================== */

const limitClause = Diagram.Diagram(
  Seq(
    T('LIMIT'),
    NT('number')
  )
);

saveDiagram(limitClause, 'limit_clause.svg');

/* ====================
   17. OFFSET Clause
   ==================== */

const offsetClause = Diagram.Diagram(
  Seq(
    T('OFFSET'),
    NT('number')
  )
);

saveDiagram(offsetClause, 'offset_clause.svg');

/* ====================
   18. Value
   ==================== */

const value = Diagram.Diagram(
  Choice(
    0,
    NT('string_literal'),
    NT('number'),
    NT('identifier')
  )
);

saveDiagram(value, 'value.svg');

/* ====================
   19. Value List
   ==================== */

const valueList = Diagram.Diagram(
  OneOrMore(NT('value'), T(','))
);

saveDiagram(valueList, 'value_list.svg');

console.log(`\n✓ Successfully generated ${fs.readdirSync(OUTPUT_DIR).length} railroad diagrams in ${OUTPUT_DIR}`);
