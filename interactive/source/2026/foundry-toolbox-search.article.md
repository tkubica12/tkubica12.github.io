---
format_version: 1
title: "Levnější a rychlejší agenti s progressive disclosure MCP přes Foundry Toolbox Search"
eyebrow: "Tool Search, auto-pin a méně input tokenů"
subtitle: "Foundry Toolbox sjednotí mnoho MCP serverů do jednoho endpointu. Tool Search k tomu přidává progressive disclosure: agent vidí nejdřív jen minimum nástrojů a plné definice si najde až ve chvíli, kdy je opravdu potřebuje."
slug: foundry-toolbox-search
date: 2026-06-09
language: cs-CZ
status: published
published: true
canonical_url: "/2026/foundry-toolbox-search/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
design:
  theme: simple-neutral
  density: presentation
---

# Levnější a rychlejší agenti s progressive disclosure MCP přes Foundry Toolbox Search

Moje testy a výsledky jsou v repozitáři [tkubica12/foundry-toolbox-search](https://github.com/tkubica12/foundry-toolbox-search).

::: group id="kapitoly" title="Od MCP schémat k úspoře tokenů"

::: card number="01" title="MCP definice a exploze vstupních tokenů" default="open"

MCP funguje tak, že agentovi - přesněji řečeno harness systému nebo MCP klientovi - pošle seznam všech nástrojů, popisů k čemu slouží a jak se používají a také případné atributy, co očekávají na vstupu a jejich vysvětlení. Celé to může vypadat nějak takhle.

::: reveal title="Standardní MCP tools/list - ukázka JSON"
```json label="measurement/context/standalone-mcp-tools.json"
{
  "loans": [
    {
      "name": "get_mortgage_affordability",
      "title": null,
      "description": "Estimate mortgage affordability for a customer.\n\n    Args:\n        customer_id: Customer identifier.\n        annual_income: Gross yearly income.\n        monthly_debt: Existing monthly debt payments.\n    ",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "annual_income": {
            "title": "Annual Income",
            "type": "number"
          },
          "monthly_debt": {
            "title": "Monthly Debt",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "annual_income",
          "monthly_debt"
        ],
        "title": "get_mortgage_affordabilityArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "quote_personal_loan",
      "title": null,
      "description": "Quote a mocked personal loan rate and payment.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "amount": {
            "title": "Amount",
            "type": "number"
          },
          "term_months": {
            "title": "Term Months",
            "type": "integer"
          }
        },
        "required": [
          "customer_id",
          "amount",
          "term_months"
        ],
        "title": "quote_personal_loanArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "check_loan_eligibility",
      "title": null,
      "description": "Check high-level eligibility for a loan product.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "product_type": {
            "title": "Product Type",
            "type": "string"
          },
          "credit_score": {
            "title": "Credit Score",
            "type": "integer"
          }
        },
        "required": [
          "customer_id",
          "product_type",
          "credit_score"
        ],
        "title": "check_loan_eligibilityArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "get_loan_balance",
      "title": null,
      "description": "Return current mocked balance for a loan.",
      "inputSchema": {
        "properties": {
          "loan_id": {
            "title": "Loan Id",
            "type": "string"
          },
          "as_of_date": {
            "title": "As Of Date",
            "type": "string"
          }
        },
        "required": [
          "loan_id",
          "as_of_date"
        ],
        "title": "get_loan_balanceArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "calculate_early_repayment_fee",
      "title": null,
      "description": "Calculate a mocked early repayment fee.",
      "inputSchema": {
        "properties": {
          "loan_id": {
            "title": "Loan Id",
            "type": "string"
          },
          "repayment_amount": {
            "title": "Repayment Amount",
            "type": "number"
          }
        },
        "required": [
          "loan_id",
          "repayment_amount"
        ],
        "title": "calculate_early_repayment_feeArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "summarize_repayment_schedule",
      "title": null,
      "description": "Summarize upcoming repayment schedule.",
      "inputSchema": {
        "properties": {
          "loan_id": {
            "title": "Loan Id",
            "type": "string"
          },
          "months": {
            "title": "Months",
            "type": "integer"
          }
        },
        "required": [
          "loan_id",
          "months"
        ],
        "title": "summarize_repayment_scheduleArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "assess_refinance_savings",
      "title": null,
      "description": "Estimate savings from refinancing.",
      "inputSchema": {
        "properties": {
          "loan_id": {
            "title": "Loan Id",
            "type": "string"
          },
          "new_apr_percent": {
            "title": "New Apr Percent",
            "type": "number"
          },
          "remaining_months": {
            "title": "Remaining Months",
            "type": "integer"
          }
        },
        "required": [
          "loan_id",
          "new_apr_percent",
          "remaining_months"
        ],
        "title": "assess_refinance_savingsArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "get_collateral_valuation",
      "title": null,
      "description": "Return mocked collateral valuation.",
      "inputSchema": {
        "properties": {
          "collateral_id": {
            "title": "Collateral Id",
            "type": "string"
          },
          "valuation_date": {
            "title": "Valuation Date",
            "type": "string"
          }
        },
        "required": [
          "collateral_id",
          "valuation_date"
        ],
        "title": "get_collateral_valuationArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "compute_ltv_ratio",
      "title": null,
      "description": "Compute loan-to-value ratio.",
      "inputSchema": {
        "properties": {
          "loan_id": {
            "title": "Loan Id",
            "type": "string"
          },
          "balance": {
            "title": "Balance",
            "type": "number"
          },
          "collateral_value": {
            "title": "Collateral Value",
            "type": "number"
          }
        },
        "required": [
          "loan_id",
          "balance",
          "collateral_value"
        ],
        "title": "compute_ltv_ratioArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "get_delinquency_status",
      "title": null,
      "description": "Return mocked delinquency status.",
      "inputSchema": {
        "properties": {
          "loan_id": {
            "title": "Loan Id",
            "type": "string"
          }
        },
        "required": [
          "loan_id"
        ],
        "title": "get_delinquency_statusArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "recommend_hardship_options",
      "title": null,
      "description": "Recommend hardship options for a borrower.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "loan_id": {
            "title": "Loan Id",
            "type": "string"
          },
          "hardship_reason": {
            "title": "Hardship Reason",
            "type": "string"
          }
        },
        "required": [
          "customer_id",
          "loan_id",
          "hardship_reason"
        ],
        "title": "recommend_hardship_optionsArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "verify_income_document",
      "title": null,
      "description": "Mock verification of income evidence.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "document_type": {
            "title": "Document Type",
            "type": "string"
          },
          "monthly_income": {
            "title": "Monthly Income",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "document_type",
          "monthly_income"
        ],
        "title": "verify_income_documentArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "estimate_debt_to_income",
      "title": null,
      "description": "Calculate debt-to-income ratio.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "annual_income": {
            "title": "Annual Income",
            "type": "number"
          },
          "monthly_debt": {
            "title": "Monthly Debt",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "annual_income",
          "monthly_debt"
        ],
        "title": "estimate_debt_to_incomeArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "get_rate_lock_status",
      "title": null,
      "description": "Return mocked rate lock status for an application.",
      "inputSchema": {
        "properties": {
          "application_id": {
            "title": "Application Id",
            "type": "string"
          }
        },
        "required": [
          "application_id"
        ],
        "title": "get_rate_lock_statusArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "create_loan_application",
      "title": null,
      "description": "Create a mocked loan application.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "product_type": {
            "title": "Product Type",
            "type": "string"
          },
          "requested_amount": {
            "title": "Requested Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "product_type",
          "requested_amount"
        ],
        "title": "create_loan_applicationArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "get_application_status",
      "title": null,
      "description": "Return mocked loan application status.",
      "inputSchema": {
        "properties": {
          "application_id": {
            "title": "Application Id",
            "type": "string"
          }
        },
        "required": [
          "application_id"
        ],
        "title": "get_application_statusArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "calculate_payoff_quote",
      "title": null,
      "description": "Calculate mocked loan payoff quote.",
      "inputSchema": {
        "properties": {
          "loan_id": {
            "title": "Loan Id",
            "type": "string"
          },
          "payoff_date": {
            "title": "Payoff Date",
            "type": "string"
          }
        },
        "required": [
          "loan_id",
          "payoff_date"
        ],
        "title": "calculate_payoff_quoteArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "compare_fixed_variable_rates",
      "title": null,
      "description": "Compare mocked fixed and variable loan options.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "amount": {
            "title": "Amount",
            "type": "number"
          },
          "term_months": {
            "title": "Term Months",
            "type": "integer"
          }
        },
        "required": [
          "customer_id",
          "amount",
          "term_months"
        ],
        "title": "compare_fixed_variable_ratesArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "list_required_loan_documents",
      "title": null,
      "description": "List required documents for a loan product.",
      "inputSchema": {
        "properties": {
          "product_type": {
            "title": "Product Type",
            "type": "string"
          },
          "customer_segment": {
            "title": "Customer Segment",
            "type": "string"
          }
        },
        "required": [
          "product_type",
          "customer_segment"
        ],
        "title": "list_required_loan_documentsArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "simulate_interest_rate_shock",
      "title": null,
      "description": "Simulate payment impact of an interest-rate shock.",
      "inputSchema": {
        "properties": {
          "loan_id": {
            "title": "Loan Id",
            "type": "string"
          },
          "shock_bps": {
            "title": "Shock Bps",
            "type": "integer"
          }
        },
        "required": [
          "loan_id",
          "shock_bps"
        ],
        "title": "simulate_interest_rate_shockArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "price_bridge_loan",
      "title": null,
      "description": "Price a short-term bridge loan for property purchase timing gaps.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "reference_id": {
            "title": "Reference Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "reference_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "assess_construction_draw",
      "title": null,
      "description": "Assess whether a construction loan draw request is in policy.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "reference_id": {
            "title": "Reference Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "reference_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "review_appraisal_gap",
      "title": null,
      "description": "Review appraisal gap risk for a mortgage application.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "reference_id": {
            "title": "Reference Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "reference_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "estimate_closing_costs",
      "title": null,
      "description": "Estimate closing costs for a loan transaction.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "reference_id": {
            "title": "Reference Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "reference_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "calculate_apr_from_fees",
      "title": null,
      "description": "Calculate annual percentage rate impact from fees.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "reference_id": {
            "title": "Reference Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "reference_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "score_small_business_loan",
      "title": null,
      "description": "Score a small-business loan using mocked financial indicators.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "reference_id": {
            "title": "Reference Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "reference_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "review_covenant_compliance",
      "title": null,
      "description": "Review mocked covenant compliance for a commercial loan.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "reference_id": {
            "title": "Reference Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "reference_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "estimate_collateral_haircut",
      "title": null,
      "description": "Estimate collateral haircut for secured lending.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "reference_id": {
            "title": "Reference Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "reference_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "calculate_balloon_payment",
      "title": null,
      "description": "Calculate mocked balloon payment for a loan.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "reference_id": {
            "title": "Reference Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "reference_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "assess_guarantor_strength",
      "title": null,
      "description": "Assess guarantor strength for a credit application.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "reference_id": {
            "title": "Reference Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "reference_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "review_payment_holiday_request",
      "title": null,
      "description": "Review a borrower payment holiday request.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "reference_id": {
            "title": "Reference Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "reference_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "calculate_interest_only_payment",
      "title": null,
      "description": "Calculate interest-only loan payment.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "reference_id": {
            "title": "Reference Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "reference_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "check_mortgage_insurance_need",
      "title": null,
      "description": "Check whether mortgage insurance is needed.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "reference_id": {
            "title": "Reference Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "reference_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "estimate_credit_line_utilization",
      "title": null,
      "description": "Estimate credit line utilization and warning status.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "reference_id": {
            "title": "Reference Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "reference_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "review_overpayment_allowance",
      "title": null,
      "description": "Review annual loan overpayment allowance.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "reference_id": {
            "title": "Reference Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "reference_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "calculate_variable_rate_reset",
      "title": null,
      "description": "Calculate payment impact at variable-rate reset.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "reference_id": {
            "title": "Reference Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "reference_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "assess_green_mortgage_discount",
      "title": null,
      "description": "Assess eligibility for green mortgage discount.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "reference_id": {
            "title": "Reference Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "reference_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "review_debt_consolidation_fit",
      "title": null,
      "description": "Review whether debt consolidation loan is suitable.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "reference_id": {
            "title": "Reference Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "reference_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "estimate_auto_loan_residual",
      "title": null,
      "description": "Estimate residual value for an auto loan.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "reference_id": {
            "title": "Reference Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "reference_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "calculate_loan_modification_terms",
      "title": null,
      "description": "Calculate mocked loan modification terms.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "reference_id": {
            "title": "Reference Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "reference_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "review_lien_position",
      "title": null,
      "description": "Review lien position for secured lending.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "reference_id": {
            "title": "Reference Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "reference_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "estimate_loss_given_default",
      "title": null,
      "description": "Estimate mocked loss given default.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "reference_id": {
            "title": "Reference Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "reference_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "calculate_probability_of_default",
      "title": null,
      "description": "Calculate mocked probability of default.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "reference_id": {
            "title": "Reference Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "reference_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "review_document_exceptions",
      "title": null,
      "description": "Review loan document exceptions.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "reference_id": {
            "title": "Reference Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "reference_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "assess_portfolio_concentration",
      "title": null,
      "description": "Assess loan portfolio concentration risk.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "reference_id": {
            "title": "Reference Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "reference_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "calculate_servicing_fee",
      "title": null,
      "description": "Calculate mocked loan servicing fee.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "reference_id": {
            "title": "Reference Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "reference_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "review_drawdown_conditions",
      "title": null,
      "description": "Review conditions precedent for loan drawdown.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "reference_id": {
            "title": "Reference Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "reference_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "estimate_prepayment_speed",
      "title": null,
      "description": "Estimate mocked prepayment speed.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "reference_id": {
            "title": "Reference Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "reference_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "check_regulatory_lending_limit",
      "title": null,
      "description": "Check regulatory lending limit headroom.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "reference_id": {
            "title": "Reference Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "reference_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "summarize_credit_memo",
      "title": null,
      "description": "Summarize mocked credit memo highlights.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "reference_id": {
            "title": "Reference Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "reference_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    }
  ],
  "investments": [
    {
      "name": "get_portfolio_summary",
      "title": null,
      "description": "Return mocked portfolio summary.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          }
        },
        "required": [
          "customer_id",
          "portfolio_id"
        ],
        "title": "get_portfolio_summaryArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "calculate_asset_allocation",
      "title": null,
      "description": "Calculate mocked asset allocation.",
      "inputSchema": {
        "properties": {
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          }
        },
        "required": [
          "portfolio_id"
        ],
        "title": "calculate_asset_allocationArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "assess_risk_profile",
      "title": null,
      "description": "Assess investor risk profile.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "horizon_years": {
            "title": "Horizon Years",
            "type": "integer"
          },
          "loss_tolerance_percent": {
            "title": "Loss Tolerance Percent",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "horizon_years",
          "loss_tolerance_percent"
        ],
        "title": "assess_risk_profileArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "recommend_rebalance_trades",
      "title": null,
      "description": "Recommend mocked rebalancing trades.",
      "inputSchema": {
        "properties": {
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "target_equity_percent": {
            "title": "Target Equity Percent",
            "type": "number"
          }
        },
        "required": [
          "portfolio_id",
          "target_equity_percent"
        ],
        "title": "recommend_rebalance_tradesArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "estimate_portfolio_var",
      "title": null,
      "description": "Estimate mocked portfolio value at risk.",
      "inputSchema": {
        "properties": {
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "confidence_percent": {
            "title": "Confidence Percent",
            "type": "number"
          },
          "horizon_days": {
            "title": "Horizon Days",
            "type": "integer"
          }
        },
        "required": [
          "portfolio_id",
          "confidence_percent",
          "horizon_days"
        ],
        "title": "estimate_portfolio_varArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "get_security_quote",
      "title": null,
      "description": "Return mocked security quote.",
      "inputSchema": {
        "properties": {
          "symbol": {
            "title": "Symbol",
            "type": "string"
          },
          "exchange": {
            "title": "Exchange",
            "type": "string"
          }
        },
        "required": [
          "symbol",
          "exchange"
        ],
        "title": "get_security_quoteArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "screen_sustainable_funds",
      "title": null,
      "description": "Screen mocked sustainable funds.",
      "inputSchema": {
        "properties": {
          "region": {
            "title": "Region",
            "type": "string"
          },
          "minimum_esg_score": {
            "title": "Minimum Esg Score",
            "type": "integer"
          },
          "asset_class": {
            "title": "Asset Class",
            "type": "string"
          }
        },
        "required": [
          "region",
          "minimum_esg_score",
          "asset_class"
        ],
        "title": "screen_sustainable_fundsArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "calculate_realized_gain",
      "title": null,
      "description": "Calculate mocked realized gains.",
      "inputSchema": {
        "properties": {
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "tax_year": {
            "title": "Tax Year",
            "type": "integer"
          }
        },
        "required": [
          "account_id",
          "tax_year"
        ],
        "title": "calculate_realized_gainArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "check_product_suitability",
      "title": null,
      "description": "Check mocked investment product suitability.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "product_id": {
            "title": "Product Id",
            "type": "string"
          },
          "risk_rating": {
            "title": "Risk Rating",
            "type": "integer"
          }
        },
        "required": [
          "customer_id",
          "product_id",
          "risk_rating"
        ],
        "title": "check_product_suitabilityArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "get_dividend_calendar",
      "title": null,
      "description": "Return mocked upcoming dividends.",
      "inputSchema": {
        "properties": {
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "next_days": {
            "title": "Next Days",
            "type": "integer"
          }
        },
        "required": [
          "portfolio_id",
          "next_days"
        ],
        "title": "get_dividend_calendarArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "simulate_market_shock",
      "title": null,
      "description": "Simulate mocked market shock impact.",
      "inputSchema": {
        "properties": {
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "equity_shock_percent": {
            "title": "Equity Shock Percent",
            "type": "number"
          },
          "rate_shock_bps": {
            "title": "Rate Shock Bps",
            "type": "integer"
          }
        },
        "required": [
          "portfolio_id",
          "equity_shock_percent",
          "rate_shock_bps"
        ],
        "title": "simulate_market_shockArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "get_investment_policy_statement",
      "title": null,
      "description": "Return mocked investment policy statement summary.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          }
        },
        "required": [
          "customer_id"
        ],
        "title": "get_investment_policy_statementArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "compare_fund_expenses",
      "title": null,
      "description": "Compare mocked fund expenses.",
      "inputSchema": {
        "properties": {
          "fund_a": {
            "title": "Fund A",
            "type": "string"
          },
          "fund_b": {
            "title": "Fund B",
            "type": "string"
          },
          "investment_amount": {
            "title": "Investment Amount",
            "type": "number"
          }
        },
        "required": [
          "fund_a",
          "fund_b",
          "investment_amount"
        ],
        "title": "compare_fund_expensesArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "calculate_expected_income",
      "title": null,
      "description": "Calculate mocked expected portfolio income.",
      "inputSchema": {
        "properties": {
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "next_months": {
            "title": "Next Months",
            "type": "integer"
          }
        },
        "required": [
          "portfolio_id",
          "next_months"
        ],
        "title": "calculate_expected_incomeArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "get_model_portfolio",
      "title": null,
      "description": "Return mocked model portfolio.",
      "inputSchema": {
        "properties": {
          "model_name": {
            "title": "Model Name",
            "type": "string"
          },
          "risk_level": {
            "title": "Risk Level",
            "type": "string"
          }
        },
        "required": [
          "model_name",
          "risk_level"
        ],
        "title": "get_model_portfolioArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "assess_concentration_risk",
      "title": null,
      "description": "Assess mocked issuer concentration risk.",
      "inputSchema": {
        "properties": {
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "issuer_limit_percent": {
            "title": "Issuer Limit Percent",
            "type": "number"
          }
        },
        "required": [
          "portfolio_id",
          "issuer_limit_percent"
        ],
        "title": "assess_concentration_riskArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "generate_trade_ticket",
      "title": null,
      "description": "Generate a mocked trade ticket.",
      "inputSchema": {
        "properties": {
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "symbol": {
            "title": "Symbol",
            "type": "string"
          },
          "side": {
            "title": "Side",
            "type": "string"
          },
          "quantity": {
            "title": "Quantity",
            "type": "integer"
          }
        },
        "required": [
          "account_id",
          "symbol",
          "side",
          "quantity"
        ],
        "title": "generate_trade_ticketArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "get_benchmark_performance",
      "title": null,
      "description": "Return mocked benchmark performance.",
      "inputSchema": {
        "properties": {
          "benchmark_id": {
            "title": "Benchmark Id",
            "type": "string"
          },
          "period": {
            "title": "Period",
            "type": "string"
          }
        },
        "required": [
          "benchmark_id",
          "period"
        ],
        "title": "get_benchmark_performanceArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "evaluate_liquidity_needs",
      "title": null,
      "description": "Evaluate mocked liquidity needs.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "required_cash": {
            "title": "Required Cash",
            "type": "number"
          },
          "horizon_months": {
            "title": "Horizon Months",
            "type": "integer"
          }
        },
        "required": [
          "customer_id",
          "required_cash",
          "horizon_months"
        ],
        "title": "evaluate_liquidity_needsArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "recommend_tax_loss_harvest",
      "title": null,
      "description": "Recommend mocked tax-loss harvesting candidates.",
      "inputSchema": {
        "properties": {
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "minimum_loss": {
            "title": "Minimum Loss",
            "type": "number"
          }
        },
        "required": [
          "portfolio_id",
          "minimum_loss"
        ],
        "title": "recommend_tax_loss_harvestArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "screen_bond_ladder",
      "title": null,
      "description": "Screen a bond ladder for maturity and income targets.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "portfolio_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "estimate_duration_risk",
      "title": null,
      "description": "Estimate duration risk for a fixed-income allocation.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "portfolio_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "calculate_sharpe_ratio",
      "title": null,
      "description": "Calculate mocked Sharpe ratio for a portfolio.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "portfolio_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "calculate_sortino_ratio",
      "title": null,
      "description": "Calculate mocked Sortino ratio for a portfolio.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "portfolio_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "review_fund_overlap",
      "title": null,
      "description": "Review overlap between funds in a portfolio.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "portfolio_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "assess_currency_exposure",
      "title": null,
      "description": "Assess currency exposure in a portfolio.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "portfolio_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "recommend_cash_allocation",
      "title": null,
      "description": "Recommend cash allocation based on liquidity need.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "portfolio_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "estimate_drawdown_risk",
      "title": null,
      "description": "Estimate potential drawdown risk.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "portfolio_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "review_structured_note",
      "title": null,
      "description": "Review suitability of a structured note.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "portfolio_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "calculate_yield_to_maturity",
      "title": null,
      "description": "Calculate mocked yield to maturity.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "portfolio_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "estimate_total_expense_ratio",
      "title": null,
      "description": "Estimate total portfolio expense ratio.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "portfolio_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "review_private_market_commitment",
      "title": null,
      "description": "Review private market commitment pacing.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "portfolio_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "assess_factor_exposure",
      "title": null,
      "description": "Assess factor exposure such as value or momentum.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "portfolio_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "calculate_tracking_error",
      "title": null,
      "description": "Calculate tracking error versus a benchmark.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "portfolio_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "recommend_glide_path",
      "title": null,
      "description": "Recommend target-date glide path allocation.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "portfolio_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "screen_income_stocks",
      "title": null,
      "description": "Screen income stocks for dividend yield.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "portfolio_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "estimate_tax_drag",
      "title": null,
      "description": "Estimate tax drag on portfolio returns.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "portfolio_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "review_restricted_list",
      "title": null,
      "description": "Review whether a security is on restricted list.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "portfolio_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "calculate_portfolio_beta",
      "title": null,
      "description": "Calculate mocked portfolio beta.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "portfolio_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "assess_alternative_allocation",
      "title": null,
      "description": "Assess alternative investment allocation.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "portfolio_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "review_margin_requirement",
      "title": null,
      "description": "Review margin requirement for a trade.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "portfolio_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "estimate_scenario_return",
      "title": null,
      "description": "Estimate portfolio return under a scenario.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "portfolio_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "calculate_required_minimum_distribution",
      "title": null,
      "description": "Calculate mocked retirement distribution.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "portfolio_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "review_client_investment_objective",
      "title": null,
      "description": "Review client investment objective alignment.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "portfolio_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "screen_low_volatility_etfs",
      "title": null,
      "description": "Screen low-volatility ETF candidates.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "portfolio_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "estimate_reinvestment_income",
      "title": null,
      "description": "Estimate reinvestment income.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "portfolio_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "calculate_capital_gains_budget",
      "title": null,
      "description": "Calculate capital gains budget.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "portfolio_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "review_portfolio_turnover",
      "title": null,
      "description": "Review portfolio turnover.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "portfolio_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "assess_fiduciary_watchlist",
      "title": null,
      "description": "Assess fiduciary watchlist items.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "portfolio_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "summarize_investment_proposal",
      "title": null,
      "description": "Summarize mocked investment proposal highlights.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "portfolio_id": {
            "title": "Portfolio Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "portfolio_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    }
  ],
  "accounts": [
    {
      "name": "get_account_balance",
      "title": null,
      "description": "Return mocked current account balance.",
      "inputSchema": {
        "properties": {
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "as_of_date": {
            "title": "As Of Date",
            "type": "string"
          }
        },
        "required": [
          "account_id",
          "as_of_date"
        ],
        "title": "get_account_balanceArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "list_recent_transactions",
      "title": null,
      "description": "List mocked recent transactions.",
      "inputSchema": {
        "properties": {
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "days": {
            "title": "Days",
            "type": "integer"
          }
        },
        "required": [
          "account_id",
          "days"
        ],
        "title": "list_recent_transactionsArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "categorize_transaction",
      "title": null,
      "description": "Categorize a transaction.",
      "inputSchema": {
        "properties": {
          "transaction_id": {
            "title": "Transaction Id",
            "type": "string"
          },
          "merchant_name": {
            "title": "Merchant Name",
            "type": "string"
          },
          "amount": {
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "transaction_id",
          "merchant_name",
          "amount"
        ],
        "title": "categorize_transactionArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "detect_overdraft_risk",
      "title": null,
      "description": "Assess mocked overdraft risk.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "projected_debits": {
            "title": "Projected Debits",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id",
          "projected_debits"
        ],
        "title": "detect_overdraft_riskArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "create_payment_instruction",
      "title": null,
      "description": "Create a mocked payment instruction.",
      "inputSchema": {
        "properties": {
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "beneficiary_iban": {
            "title": "Beneficiary Iban",
            "type": "string"
          },
          "amount": {
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "account_id",
          "beneficiary_iban",
          "amount"
        ],
        "title": "create_payment_instructionArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "validate_iban",
      "title": null,
      "description": "Validate an IBAN format at a mocked level.",
      "inputSchema": {
        "properties": {
          "iban": {
            "title": "Iban",
            "type": "string"
          },
          "country_code": {
            "title": "Country Code",
            "type": "string"
          }
        },
        "required": [
          "iban",
          "country_code"
        ],
        "title": "validate_ibanArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "get_direct_debits",
      "title": null,
      "description": "Return mocked direct debits.",
      "inputSchema": {
        "properties": {
          "account_id": {
            "title": "Account Id",
            "type": "string"
          }
        },
        "required": [
          "account_id"
        ],
        "title": "get_direct_debitsArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "summarize_cash_flow",
      "title": null,
      "description": "Summarize cash flow for a date range.",
      "inputSchema": {
        "properties": {
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "start_date": {
            "title": "Start Date",
            "type": "string"
          },
          "end_date": {
            "title": "End Date",
            "type": "string"
          }
        },
        "required": [
          "account_id",
          "start_date",
          "end_date"
        ],
        "title": "summarize_cash_flowArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "flag_unusual_spend",
      "title": null,
      "description": "Flag unusually high spend.",
      "inputSchema": {
        "properties": {
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "category": {
            "title": "Category",
            "type": "string"
          },
          "amount": {
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "account_id",
          "category",
          "amount"
        ],
        "title": "flag_unusual_spendArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "get_card_status",
      "title": null,
      "description": "Return card status.",
      "inputSchema": {
        "properties": {
          "card_id": {
            "title": "Card Id",
            "type": "string"
          }
        },
        "required": [
          "card_id"
        ],
        "title": "get_card_statusArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "freeze_card",
      "title": null,
      "description": "Mock freezing a card.",
      "inputSchema": {
        "properties": {
          "card_id": {
            "title": "Card Id",
            "type": "string"
          },
          "reason": {
            "title": "Reason",
            "type": "string"
          }
        },
        "required": [
          "card_id",
          "reason"
        ],
        "title": "freeze_cardArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "calculate_monthly_fees",
      "title": null,
      "description": "Calculate mocked monthly account fees.",
      "inputSchema": {
        "properties": {
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "month": {
            "title": "Month",
            "type": "string"
          }
        },
        "required": [
          "account_id",
          "month"
        ],
        "title": "calculate_monthly_feesArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "check_account_kyc_status",
      "title": null,
      "description": "Return KYC status for current account servicing.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          }
        },
        "required": [
          "customer_id"
        ],
        "title": "check_account_kyc_statusArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "get_savings_sweep_recommendation",
      "title": null,
      "description": "Recommend a sweep from current account to savings.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "minimum_buffer": {
            "title": "Minimum Buffer",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id",
          "minimum_buffer"
        ],
        "title": "get_savings_sweep_recommendationArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "estimate_foreign_exchange_fee",
      "title": null,
      "description": "Estimate FX fee for account transaction.",
      "inputSchema": {
        "properties": {
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "source_currency": {
            "title": "Source Currency",
            "type": "string"
          },
          "target_currency": {
            "title": "Target Currency",
            "type": "string"
          },
          "amount": {
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "account_id",
          "source_currency",
          "target_currency",
          "amount"
        ],
        "title": "estimate_foreign_exchange_feeArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "get_standing_orders",
      "title": null,
      "description": "List mocked standing orders.",
      "inputSchema": {
        "properties": {
          "account_id": {
            "title": "Account Id",
            "type": "string"
          }
        },
        "required": [
          "account_id"
        ],
        "title": "get_standing_ordersArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "project_end_of_month_balance",
      "title": null,
      "description": "Project end-of-month balance.",
      "inputSchema": {
        "properties": {
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "expected_income": {
            "title": "Expected Income",
            "type": "number"
          },
          "expected_spend": {
            "title": "Expected Spend",
            "type": "number"
          }
        },
        "required": [
          "account_id",
          "expected_income",
          "expected_spend"
        ],
        "title": "project_end_of_month_balanceArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "find_duplicate_charges",
      "title": null,
      "description": "Find mocked duplicate charges.",
      "inputSchema": {
        "properties": {
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "lookback_days": {
            "title": "Lookback Days",
            "type": "integer"
          }
        },
        "required": [
          "account_id",
          "lookback_days"
        ],
        "title": "find_duplicate_chargesArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "get_account_alert_preferences",
      "title": null,
      "description": "Return account alert preferences.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          }
        },
        "required": [
          "customer_id",
          "account_id"
        ],
        "title": "get_account_alert_preferencesArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "recommend_fee_waiver",
      "title": null,
      "description": "Recommend whether to waive account fees.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "relationship_years": {
            "title": "Relationship Years",
            "type": "integer"
          }
        },
        "required": [
          "customer_id",
          "account_id",
          "relationship_years"
        ],
        "title": "recommend_fee_waiverArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "review_payment_limit",
      "title": null,
      "description": "Review payment limit for a current account.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "increase_transfer_limit",
      "title": null,
      "description": "Mock increasing transfer limit.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "assess_salary_pattern",
      "title": null,
      "description": "Assess salary pattern in current account transactions.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "detect_subscription_spend",
      "title": null,
      "description": "Detect recurring subscription spend.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "summarize_merchant_spend",
      "title": null,
      "description": "Summarize spend by merchant.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "review_chargeback_case",
      "title": null,
      "description": "Review card chargeback case.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "create_card_replacement",
      "title": null,
      "description": "Create mocked card replacement order.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "estimate_cash_withdrawal_fee",
      "title": null,
      "description": "Estimate cash withdrawal fee.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "review_joint_account_access",
      "title": null,
      "description": "Review joint account access status.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "check_sepa_reachability",
      "title": null,
      "description": "Check SEPA reachability for a beneficiary.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "validate_payment_reference",
      "title": null,
      "description": "Validate payment reference format.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "assess_fraud_alert",
      "title": null,
      "description": "Assess mocked fraud alert.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "review_account_closure_readiness",
      "title": null,
      "description": "Review account closure readiness.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "calculate_interest_on_positive_balance",
      "title": null,
      "description": "Calculate interest on positive balance.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "recommend_budget_category_limit",
      "title": null,
      "description": "Recommend budget category limit.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "detect_income_interruption",
      "title": null,
      "description": "Detect income interruption risk.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "review_cash_deposit_pattern",
      "title": null,
      "description": "Review cash deposit pattern.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "estimate_international_transfer_time",
      "title": null,
      "description": "Estimate international transfer time.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "check_beneficiary_risk",
      "title": null,
      "description": "Check beneficiary risk score.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "review_power_of_attorney",
      "title": null,
      "description": "Review power of attorney on account.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "summarize_monthly_statement",
      "title": null,
      "description": "Summarize monthly current account statement.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "detect_round_number_transfers",
      "title": null,
      "description": "Detect round-number transfer pattern.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "review_account_package_fit",
      "title": null,
      "description": "Review current account package fit.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "estimate_atm_rebate",
      "title": null,
      "description": "Estimate ATM fee rebate.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "check_dormancy_risk",
      "title": null,
      "description": "Check account dormancy risk.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "review_negative_balance_history",
      "title": null,
      "description": "Review negative balance history.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "recommend_alert_threshold",
      "title": null,
      "description": "Recommend balance alert threshold.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "assess_travel_notice_need",
      "title": null,
      "description": "Assess whether travel notice is needed.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "review_cashback_eligibility",
      "title": null,
      "description": "Review cashback eligibility.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    },
    {
      "name": "summarize_account_health",
      "title": null,
      "description": "Summarize mocked account health.",
      "inputSchema": {
        "properties": {
          "customer_id": {
            "title": "Customer Id",
            "type": "string"
          },
          "account_id": {
            "title": "Account Id",
            "type": "string"
          },
          "amount": {
            "default": 1000.0,
            "title": "Amount",
            "type": "number"
          }
        },
        "required": [
          "customer_id",
          "account_id"
        ],
        "title": "toolArguments",
        "type": "object"
      },
      "outputSchema": null,
      "icons": null,
      "annotations": null,
      "meta": null,
      "execution": null
    }
  ]
}
```
:::

V demu jsou tři samostatné MCP servery pro FSI domény: `loans`, `investments` a `accounts`. Raw `tools/list` z těchto serverů je uložený v [`standalone-mcp-tools.json`](https://github.com/tkubica12/foundry-toolbox-search/blob/main/measurement/context/standalone-mcp-tools.json).

Vypadá to nevinně, ale jsou tu hned dva praktické problémy.

::: tabs id="mcp-problems"

::: tab id="tokeny" title="Tokeny"
**Definice nástrojů zabírají hodně místa v kontextu.**

První problém samozřejmě je, že tohle je opravdu hodně textu a ten jde do vstupních tokenů bez ohledu na to, který nástroj pak agent reálně použije a dokonce i v případě, že se rozhodne nepoužít žádný. Takže uživatelovo:

```text label="Uživatel"
Ahoj
```

a odpověď:

```text label="Agent"
Ahoj, co pro tebe můžu udělat?
```

znamená klidně i tisíce vstupních tokenů, jejich náklady a zvýšení času do prvního tokenu.
:::

::: tab id="sprava-endpointu" title="Správa endpointů"
**Různé MCP servery mají různé URL, přístupy a katalog.**

Druhou potíží je to, že MCP serverů může být několik, mají různé URL, přístupy, katalog a dává smysl tohle sjednotit. Ideálně vytvořit krabici na nářadí, toolbox, který obsahuje vhodné MCP servery pro danou úlohu.
:::

:::

::: callout type="verdict" title="Foundry"
S oběma problémy nám pomůže Foundry Toolbox, pojďme se na něj podívat.
:::

:::

::: card number="02" title="Foundry Toolbox"

Foundry je Microsoft platforma pro standardizovanou otevřenou tvorbu agentských řešení, chatbotů nebo AI workflow a rutin. Přináší runtime pro agenty, hostování runtime třetích stran v sandboxu, modely, observabilitu, guardrails, evaluations, red teaming, paměť a další platformní komponenty. Jednou z nich jsou právě nástroje a možnost je spravovat v rámci platformy naskládáním do instalatérského boxu.

::: steps title="Mentální model"
1. **MCP servery** - jednotlivé doménové capability, často s mnoha tools.
2. **Foundry Toolbox** - katalog a jeden MCP endpoint nad těmito capability.
3. **Tool Search** - malá vstupní sada tools (`tool_search`, `call_tool`) a dohledání plných definic až podle potřeby.
4. **Auto-pin** - často používané tools se po zahřátí objeví v kontextu rovnou.
:::

V rámci sekce Build ve Foundry portálu se můžeme podívat na Tools, kde žijí jednak jednotlivé nástroje, ale i Skills a nad tím vším zmíněné Toolboxy.

![Foundry Tools v sekci Build](/images/2026/ZoomIt%202026-06-08%20130657.png)

Nástroje můžu vybrat z katalogu.

![Katalog nástrojů ve Foundry](/images/2026/ZoomIt%202026-06-08%20130955.png)

Nebo použít vlastní API volání, A2A (komunikace na jiného agenta jako nástroj), nebo MCP, což byl můj případ.

![Vlastní nástroje, A2A a MCP](/images/2026/ZoomIt%202026-06-08%20131121.png)

Použil jsem celkem tři MCP servery, které jsem nasadil do Azure Container App. Jde o servery představující bankovní oblasti, konkrétně accounts, investments a loans a mají pro demo účely namockované odpovědi. Například pro loans mám volání jako je `get_mortgage_affordability` nebo `calculate_early_repayment_fee`.

Tyto tři servery, každý obsahující 50 nástrojů, jsem napojil do toolboxu. Všimněte si důležitého bodu - mohu asociovat guardrails politiku. To se může hodit například pro hlídání PII informací nebo jailbreak pokusy (zejména pokud používám A2A pro agent as tool) a Foundry podporuje i integraci do nástrojů třetích stran jako je Palo Alto Prisma nebo Zenity.

![Toolbox se třemi MCP servery a guardrails politikou](/images/2026/ZoomIt%202026-06-08%20131501.png)

Tento toolbox můžu napojit například do Foundry Prompt agenta, Microsoft Agent Framework nebo třeba LangGraph.

![Použití toolboxu v agentských runtimes](/images/2026/ZoomIt%202026-06-08%20132003.png)

Podle dokumentace je [Foundry Toolbox](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/toolbox) curated bundle nástrojů, které nakonfigurujete jednou a vystavíte jako jeden MCP-compatible endpoint. Do toolboxu mohou patřit například MCP servery, OpenAPI tools, Azure AI Search nebo další nástroje používané Foundry Agents.

::: callout type="rule" title="Nejde jen o pohodlí"
Jedna URL pro agenta je fajn. Zajímavější je ale kontrola nad tím, **co se dostane do model contextu** a co zůstane schované za vyhledáním.
:::

:::

::: card number="03" title="Plné definice nástrojů: direct access scénář"

První scénář počítá s klasickým MCP řešením, tedy plná definice všech volání, jejich popis a atributy. Z pohledu tokenů je vcelku jedno jestli jde o separátní MCP servery nebo je sjednotíme do toolboxu, výsledek bude stejný. Jestli chcete, podívejte se na obsáhlý JSON.

::: reveal title="Co model vidí při direct access"
```json label="measurement/context/direct-agent-tools.json"
[
  {
    "type": "function",
    "name": "loans__get_mortgage_affordability",
    "description": "Estimate mortgage affordability for a customer.\n\n    Args:\n        customer_id: Customer identifier.\n        annual_income: Gross yearly income.\n        monthly_debt: Existing monthly debt payments.\n    ",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "annual_income": {
          "title": "Annual Income",
          "type": "number"
        },
        "monthly_debt": {
          "title": "Monthly Debt",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "annual_income",
        "monthly_debt"
      ],
      "title": "get_mortgage_affordabilityArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__quote_personal_loan",
    "description": "Quote a mocked personal loan rate and payment.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "amount": {
          "title": "Amount",
          "type": "number"
        },
        "term_months": {
          "title": "Term Months",
          "type": "integer"
        }
      },
      "required": [
        "customer_id",
        "amount",
        "term_months"
      ],
      "title": "quote_personal_loanArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__check_loan_eligibility",
    "description": "Check high-level eligibility for a loan product.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "product_type": {
          "title": "Product Type",
          "type": "string"
        },
        "credit_score": {
          "title": "Credit Score",
          "type": "integer"
        }
      },
      "required": [
        "customer_id",
        "product_type",
        "credit_score"
      ],
      "title": "check_loan_eligibilityArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__get_loan_balance",
    "description": "Return current mocked balance for a loan.",
    "parameters": {
      "properties": {
        "loan_id": {
          "title": "Loan Id",
          "type": "string"
        },
        "as_of_date": {
          "title": "As Of Date",
          "type": "string"
        }
      },
      "required": [
        "loan_id",
        "as_of_date"
      ],
      "title": "get_loan_balanceArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__calculate_early_repayment_fee",
    "description": "Calculate a mocked early repayment fee.",
    "parameters": {
      "properties": {
        "loan_id": {
          "title": "Loan Id",
          "type": "string"
        },
        "repayment_amount": {
          "title": "Repayment Amount",
          "type": "number"
        }
      },
      "required": [
        "loan_id",
        "repayment_amount"
      ],
      "title": "calculate_early_repayment_feeArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__summarize_repayment_schedule",
    "description": "Summarize upcoming repayment schedule.",
    "parameters": {
      "properties": {
        "loan_id": {
          "title": "Loan Id",
          "type": "string"
        },
        "months": {
          "title": "Months",
          "type": "integer"
        }
      },
      "required": [
        "loan_id",
        "months"
      ],
      "title": "summarize_repayment_scheduleArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__assess_refinance_savings",
    "description": "Estimate savings from refinancing.",
    "parameters": {
      "properties": {
        "loan_id": {
          "title": "Loan Id",
          "type": "string"
        },
        "new_apr_percent": {
          "title": "New Apr Percent",
          "type": "number"
        },
        "remaining_months": {
          "title": "Remaining Months",
          "type": "integer"
        }
      },
      "required": [
        "loan_id",
        "new_apr_percent",
        "remaining_months"
      ],
      "title": "assess_refinance_savingsArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__get_collateral_valuation",
    "description": "Return mocked collateral valuation.",
    "parameters": {
      "properties": {
        "collateral_id": {
          "title": "Collateral Id",
          "type": "string"
        },
        "valuation_date": {
          "title": "Valuation Date",
          "type": "string"
        }
      },
      "required": [
        "collateral_id",
        "valuation_date"
      ],
      "title": "get_collateral_valuationArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__compute_ltv_ratio",
    "description": "Compute loan-to-value ratio.",
    "parameters": {
      "properties": {
        "loan_id": {
          "title": "Loan Id",
          "type": "string"
        },
        "balance": {
          "title": "Balance",
          "type": "number"
        },
        "collateral_value": {
          "title": "Collateral Value",
          "type": "number"
        }
      },
      "required": [
        "loan_id",
        "balance",
        "collateral_value"
      ],
      "title": "compute_ltv_ratioArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__get_delinquency_status",
    "description": "Return mocked delinquency status.",
    "parameters": {
      "properties": {
        "loan_id": {
          "title": "Loan Id",
          "type": "string"
        }
      },
      "required": [
        "loan_id"
      ],
      "title": "get_delinquency_statusArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__recommend_hardship_options",
    "description": "Recommend hardship options for a borrower.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "loan_id": {
          "title": "Loan Id",
          "type": "string"
        },
        "hardship_reason": {
          "title": "Hardship Reason",
          "type": "string"
        }
      },
      "required": [
        "customer_id",
        "loan_id",
        "hardship_reason"
      ],
      "title": "recommend_hardship_optionsArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__verify_income_document",
    "description": "Mock verification of income evidence.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "document_type": {
          "title": "Document Type",
          "type": "string"
        },
        "monthly_income": {
          "title": "Monthly Income",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "document_type",
        "monthly_income"
      ],
      "title": "verify_income_documentArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__estimate_debt_to_income",
    "description": "Calculate debt-to-income ratio.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "annual_income": {
          "title": "Annual Income",
          "type": "number"
        },
        "monthly_debt": {
          "title": "Monthly Debt",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "annual_income",
        "monthly_debt"
      ],
      "title": "estimate_debt_to_incomeArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__get_rate_lock_status",
    "description": "Return mocked rate lock status for an application.",
    "parameters": {
      "properties": {
        "application_id": {
          "title": "Application Id",
          "type": "string"
        }
      },
      "required": [
        "application_id"
      ],
      "title": "get_rate_lock_statusArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__create_loan_application",
    "description": "Create a mocked loan application.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "product_type": {
          "title": "Product Type",
          "type": "string"
        },
        "requested_amount": {
          "title": "Requested Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "product_type",
        "requested_amount"
      ],
      "title": "create_loan_applicationArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__get_application_status",
    "description": "Return mocked loan application status.",
    "parameters": {
      "properties": {
        "application_id": {
          "title": "Application Id",
          "type": "string"
        }
      },
      "required": [
        "application_id"
      ],
      "title": "get_application_statusArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__calculate_payoff_quote",
    "description": "Calculate mocked loan payoff quote.",
    "parameters": {
      "properties": {
        "loan_id": {
          "title": "Loan Id",
          "type": "string"
        },
        "payoff_date": {
          "title": "Payoff Date",
          "type": "string"
        }
      },
      "required": [
        "loan_id",
        "payoff_date"
      ],
      "title": "calculate_payoff_quoteArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__compare_fixed_variable_rates",
    "description": "Compare mocked fixed and variable loan options.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "amount": {
          "title": "Amount",
          "type": "number"
        },
        "term_months": {
          "title": "Term Months",
          "type": "integer"
        }
      },
      "required": [
        "customer_id",
        "amount",
        "term_months"
      ],
      "title": "compare_fixed_variable_ratesArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__list_required_loan_documents",
    "description": "List required documents for a loan product.",
    "parameters": {
      "properties": {
        "product_type": {
          "title": "Product Type",
          "type": "string"
        },
        "customer_segment": {
          "title": "Customer Segment",
          "type": "string"
        }
      },
      "required": [
        "product_type",
        "customer_segment"
      ],
      "title": "list_required_loan_documentsArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__simulate_interest_rate_shock",
    "description": "Simulate payment impact of an interest-rate shock.",
    "parameters": {
      "properties": {
        "loan_id": {
          "title": "Loan Id",
          "type": "string"
        },
        "shock_bps": {
          "title": "Shock Bps",
          "type": "integer"
        }
      },
      "required": [
        "loan_id",
        "shock_bps"
      ],
      "title": "simulate_interest_rate_shockArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__price_bridge_loan",
    "description": "Price a short-term bridge loan for property purchase timing gaps.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "reference_id": {
          "title": "Reference Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "reference_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__assess_construction_draw",
    "description": "Assess whether a construction loan draw request is in policy.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "reference_id": {
          "title": "Reference Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "reference_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__review_appraisal_gap",
    "description": "Review appraisal gap risk for a mortgage application.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "reference_id": {
          "title": "Reference Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "reference_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__estimate_closing_costs",
    "description": "Estimate closing costs for a loan transaction.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "reference_id": {
          "title": "Reference Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "reference_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__calculate_apr_from_fees",
    "description": "Calculate annual percentage rate impact from fees.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "reference_id": {
          "title": "Reference Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "reference_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__score_small_business_loan",
    "description": "Score a small-business loan using mocked financial indicators.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "reference_id": {
          "title": "Reference Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "reference_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__review_covenant_compliance",
    "description": "Review mocked covenant compliance for a commercial loan.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "reference_id": {
          "title": "Reference Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "reference_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__estimate_collateral_haircut",
    "description": "Estimate collateral haircut for secured lending.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "reference_id": {
          "title": "Reference Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "reference_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__calculate_balloon_payment",
    "description": "Calculate mocked balloon payment for a loan.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "reference_id": {
          "title": "Reference Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "reference_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__assess_guarantor_strength",
    "description": "Assess guarantor strength for a credit application.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "reference_id": {
          "title": "Reference Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "reference_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__review_payment_holiday_request",
    "description": "Review a borrower payment holiday request.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "reference_id": {
          "title": "Reference Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "reference_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__calculate_interest_only_payment",
    "description": "Calculate interest-only loan payment.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "reference_id": {
          "title": "Reference Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "reference_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__check_mortgage_insurance_need",
    "description": "Check whether mortgage insurance is needed.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "reference_id": {
          "title": "Reference Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "reference_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__estimate_credit_line_utilization",
    "description": "Estimate credit line utilization and warning status.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "reference_id": {
          "title": "Reference Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "reference_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__review_overpayment_allowance",
    "description": "Review annual loan overpayment allowance.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "reference_id": {
          "title": "Reference Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "reference_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__calculate_variable_rate_reset",
    "description": "Calculate payment impact at variable-rate reset.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "reference_id": {
          "title": "Reference Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "reference_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__assess_green_mortgage_discount",
    "description": "Assess eligibility for green mortgage discount.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "reference_id": {
          "title": "Reference Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "reference_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__review_debt_consolidation_fit",
    "description": "Review whether debt consolidation loan is suitable.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "reference_id": {
          "title": "Reference Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "reference_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__estimate_auto_loan_residual",
    "description": "Estimate residual value for an auto loan.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "reference_id": {
          "title": "Reference Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "reference_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__calculate_loan_modification_terms",
    "description": "Calculate mocked loan modification terms.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "reference_id": {
          "title": "Reference Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "reference_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__review_lien_position",
    "description": "Review lien position for secured lending.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "reference_id": {
          "title": "Reference Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "reference_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__estimate_loss_given_default",
    "description": "Estimate mocked loss given default.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "reference_id": {
          "title": "Reference Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "reference_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__calculate_probability_of_default",
    "description": "Calculate mocked probability of default.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "reference_id": {
          "title": "Reference Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "reference_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__review_document_exceptions",
    "description": "Review loan document exceptions.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "reference_id": {
          "title": "Reference Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "reference_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__assess_portfolio_concentration",
    "description": "Assess loan portfolio concentration risk.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "reference_id": {
          "title": "Reference Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "reference_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__calculate_servicing_fee",
    "description": "Calculate mocked loan servicing fee.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "reference_id": {
          "title": "Reference Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "reference_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__review_drawdown_conditions",
    "description": "Review conditions precedent for loan drawdown.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "reference_id": {
          "title": "Reference Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "reference_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__estimate_prepayment_speed",
    "description": "Estimate mocked prepayment speed.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "reference_id": {
          "title": "Reference Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "reference_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__check_regulatory_lending_limit",
    "description": "Check regulatory lending limit headroom.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "reference_id": {
          "title": "Reference Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "reference_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "loans__summarize_credit_memo",
    "description": "Summarize mocked credit memo highlights.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "reference_id": {
          "title": "Reference Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "reference_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__get_portfolio_summary",
    "description": "Return mocked portfolio summary.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        }
      },
      "required": [
        "customer_id",
        "portfolio_id"
      ],
      "title": "get_portfolio_summaryArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__calculate_asset_allocation",
    "description": "Calculate mocked asset allocation.",
    "parameters": {
      "properties": {
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        }
      },
      "required": [
        "portfolio_id"
      ],
      "title": "calculate_asset_allocationArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__assess_risk_profile",
    "description": "Assess investor risk profile.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "horizon_years": {
          "title": "Horizon Years",
          "type": "integer"
        },
        "loss_tolerance_percent": {
          "title": "Loss Tolerance Percent",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "horizon_years",
        "loss_tolerance_percent"
      ],
      "title": "assess_risk_profileArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__recommend_rebalance_trades",
    "description": "Recommend mocked rebalancing trades.",
    "parameters": {
      "properties": {
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "target_equity_percent": {
          "title": "Target Equity Percent",
          "type": "number"
        }
      },
      "required": [
        "portfolio_id",
        "target_equity_percent"
      ],
      "title": "recommend_rebalance_tradesArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__estimate_portfolio_var",
    "description": "Estimate mocked portfolio value at risk.",
    "parameters": {
      "properties": {
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "confidence_percent": {
          "title": "Confidence Percent",
          "type": "number"
        },
        "horizon_days": {
          "title": "Horizon Days",
          "type": "integer"
        }
      },
      "required": [
        "portfolio_id",
        "confidence_percent",
        "horizon_days"
      ],
      "title": "estimate_portfolio_varArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__get_security_quote",
    "description": "Return mocked security quote.",
    "parameters": {
      "properties": {
        "symbol": {
          "title": "Symbol",
          "type": "string"
        },
        "exchange": {
          "title": "Exchange",
          "type": "string"
        }
      },
      "required": [
        "symbol",
        "exchange"
      ],
      "title": "get_security_quoteArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__screen_sustainable_funds",
    "description": "Screen mocked sustainable funds.",
    "parameters": {
      "properties": {
        "region": {
          "title": "Region",
          "type": "string"
        },
        "minimum_esg_score": {
          "title": "Minimum Esg Score",
          "type": "integer"
        },
        "asset_class": {
          "title": "Asset Class",
          "type": "string"
        }
      },
      "required": [
        "region",
        "minimum_esg_score",
        "asset_class"
      ],
      "title": "screen_sustainable_fundsArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__calculate_realized_gain",
    "description": "Calculate mocked realized gains.",
    "parameters": {
      "properties": {
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "tax_year": {
          "title": "Tax Year",
          "type": "integer"
        }
      },
      "required": [
        "account_id",
        "tax_year"
      ],
      "title": "calculate_realized_gainArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__check_product_suitability",
    "description": "Check mocked investment product suitability.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "product_id": {
          "title": "Product Id",
          "type": "string"
        },
        "risk_rating": {
          "title": "Risk Rating",
          "type": "integer"
        }
      },
      "required": [
        "customer_id",
        "product_id",
        "risk_rating"
      ],
      "title": "check_product_suitabilityArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__get_dividend_calendar",
    "description": "Return mocked upcoming dividends.",
    "parameters": {
      "properties": {
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "next_days": {
          "title": "Next Days",
          "type": "integer"
        }
      },
      "required": [
        "portfolio_id",
        "next_days"
      ],
      "title": "get_dividend_calendarArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__simulate_market_shock",
    "description": "Simulate mocked market shock impact.",
    "parameters": {
      "properties": {
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "equity_shock_percent": {
          "title": "Equity Shock Percent",
          "type": "number"
        },
        "rate_shock_bps": {
          "title": "Rate Shock Bps",
          "type": "integer"
        }
      },
      "required": [
        "portfolio_id",
        "equity_shock_percent",
        "rate_shock_bps"
      ],
      "title": "simulate_market_shockArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__get_investment_policy_statement",
    "description": "Return mocked investment policy statement summary.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        }
      },
      "required": [
        "customer_id"
      ],
      "title": "get_investment_policy_statementArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__compare_fund_expenses",
    "description": "Compare mocked fund expenses.",
    "parameters": {
      "properties": {
        "fund_a": {
          "title": "Fund A",
          "type": "string"
        },
        "fund_b": {
          "title": "Fund B",
          "type": "string"
        },
        "investment_amount": {
          "title": "Investment Amount",
          "type": "number"
        }
      },
      "required": [
        "fund_a",
        "fund_b",
        "investment_amount"
      ],
      "title": "compare_fund_expensesArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__calculate_expected_income",
    "description": "Calculate mocked expected portfolio income.",
    "parameters": {
      "properties": {
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "next_months": {
          "title": "Next Months",
          "type": "integer"
        }
      },
      "required": [
        "portfolio_id",
        "next_months"
      ],
      "title": "calculate_expected_incomeArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__get_model_portfolio",
    "description": "Return mocked model portfolio.",
    "parameters": {
      "properties": {
        "model_name": {
          "title": "Model Name",
          "type": "string"
        },
        "risk_level": {
          "title": "Risk Level",
          "type": "string"
        }
      },
      "required": [
        "model_name",
        "risk_level"
      ],
      "title": "get_model_portfolioArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__assess_concentration_risk",
    "description": "Assess mocked issuer concentration risk.",
    "parameters": {
      "properties": {
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "issuer_limit_percent": {
          "title": "Issuer Limit Percent",
          "type": "number"
        }
      },
      "required": [
        "portfolio_id",
        "issuer_limit_percent"
      ],
      "title": "assess_concentration_riskArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__generate_trade_ticket",
    "description": "Generate a mocked trade ticket.",
    "parameters": {
      "properties": {
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "symbol": {
          "title": "Symbol",
          "type": "string"
        },
        "side": {
          "title": "Side",
          "type": "string"
        },
        "quantity": {
          "title": "Quantity",
          "type": "integer"
        }
      },
      "required": [
        "account_id",
        "symbol",
        "side",
        "quantity"
      ],
      "title": "generate_trade_ticketArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__get_benchmark_performance",
    "description": "Return mocked benchmark performance.",
    "parameters": {
      "properties": {
        "benchmark_id": {
          "title": "Benchmark Id",
          "type": "string"
        },
        "period": {
          "title": "Period",
          "type": "string"
        }
      },
      "required": [
        "benchmark_id",
        "period"
      ],
      "title": "get_benchmark_performanceArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__evaluate_liquidity_needs",
    "description": "Evaluate mocked liquidity needs.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "required_cash": {
          "title": "Required Cash",
          "type": "number"
        },
        "horizon_months": {
          "title": "Horizon Months",
          "type": "integer"
        }
      },
      "required": [
        "customer_id",
        "required_cash",
        "horizon_months"
      ],
      "title": "evaluate_liquidity_needsArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__recommend_tax_loss_harvest",
    "description": "Recommend mocked tax-loss harvesting candidates.",
    "parameters": {
      "properties": {
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "minimum_loss": {
          "title": "Minimum Loss",
          "type": "number"
        }
      },
      "required": [
        "portfolio_id",
        "minimum_loss"
      ],
      "title": "recommend_tax_loss_harvestArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__screen_bond_ladder",
    "description": "Screen a bond ladder for maturity and income targets.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "portfolio_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__estimate_duration_risk",
    "description": "Estimate duration risk for a fixed-income allocation.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "portfolio_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__calculate_sharpe_ratio",
    "description": "Calculate mocked Sharpe ratio for a portfolio.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "portfolio_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__calculate_sortino_ratio",
    "description": "Calculate mocked Sortino ratio for a portfolio.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "portfolio_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__review_fund_overlap",
    "description": "Review overlap between funds in a portfolio.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "portfolio_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__assess_currency_exposure",
    "description": "Assess currency exposure in a portfolio.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "portfolio_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__recommend_cash_allocation",
    "description": "Recommend cash allocation based on liquidity need.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "portfolio_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__estimate_drawdown_risk",
    "description": "Estimate potential drawdown risk.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "portfolio_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__review_structured_note",
    "description": "Review suitability of a structured note.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "portfolio_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__calculate_yield_to_maturity",
    "description": "Calculate mocked yield to maturity.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "portfolio_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__estimate_total_expense_ratio",
    "description": "Estimate total portfolio expense ratio.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "portfolio_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__review_private_market_commitment",
    "description": "Review private market commitment pacing.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "portfolio_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__assess_factor_exposure",
    "description": "Assess factor exposure such as value or momentum.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "portfolio_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__calculate_tracking_error",
    "description": "Calculate tracking error versus a benchmark.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "portfolio_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__recommend_glide_path",
    "description": "Recommend target-date glide path allocation.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "portfolio_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__screen_income_stocks",
    "description": "Screen income stocks for dividend yield.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "portfolio_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__estimate_tax_drag",
    "description": "Estimate tax drag on portfolio returns.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "portfolio_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__review_restricted_list",
    "description": "Review whether a security is on restricted list.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "portfolio_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__calculate_portfolio_beta",
    "description": "Calculate mocked portfolio beta.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "portfolio_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__assess_alternative_allocation",
    "description": "Assess alternative investment allocation.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "portfolio_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__review_margin_requirement",
    "description": "Review margin requirement for a trade.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "portfolio_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__estimate_scenario_return",
    "description": "Estimate portfolio return under a scenario.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "portfolio_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__calculate_required_minimum_distribution",
    "description": "Calculate mocked retirement distribution.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "portfolio_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__review_client_investment_objective",
    "description": "Review client investment objective alignment.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "portfolio_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__screen_low_volatility_etfs",
    "description": "Screen low-volatility ETF candidates.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "portfolio_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__estimate_reinvestment_income",
    "description": "Estimate reinvestment income.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "portfolio_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__calculate_capital_gains_budget",
    "description": "Calculate capital gains budget.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "portfolio_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__review_portfolio_turnover",
    "description": "Review portfolio turnover.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "portfolio_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__assess_fiduciary_watchlist",
    "description": "Assess fiduciary watchlist items.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "portfolio_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "investments__summarize_investment_proposal",
    "description": "Summarize mocked investment proposal highlights.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "portfolio_id": {
          "title": "Portfolio Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "portfolio_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__get_account_balance",
    "description": "Return mocked current account balance.",
    "parameters": {
      "properties": {
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "as_of_date": {
          "title": "As Of Date",
          "type": "string"
        }
      },
      "required": [
        "account_id",
        "as_of_date"
      ],
      "title": "get_account_balanceArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__list_recent_transactions",
    "description": "List mocked recent transactions.",
    "parameters": {
      "properties": {
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "days": {
          "title": "Days",
          "type": "integer"
        }
      },
      "required": [
        "account_id",
        "days"
      ],
      "title": "list_recent_transactionsArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__categorize_transaction",
    "description": "Categorize a transaction.",
    "parameters": {
      "properties": {
        "transaction_id": {
          "title": "Transaction Id",
          "type": "string"
        },
        "merchant_name": {
          "title": "Merchant Name",
          "type": "string"
        },
        "amount": {
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "transaction_id",
        "merchant_name",
        "amount"
      ],
      "title": "categorize_transactionArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__detect_overdraft_risk",
    "description": "Assess mocked overdraft risk.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "projected_debits": {
          "title": "Projected Debits",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id",
        "projected_debits"
      ],
      "title": "detect_overdraft_riskArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__create_payment_instruction",
    "description": "Create a mocked payment instruction.",
    "parameters": {
      "properties": {
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "beneficiary_iban": {
          "title": "Beneficiary Iban",
          "type": "string"
        },
        "amount": {
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "account_id",
        "beneficiary_iban",
        "amount"
      ],
      "title": "create_payment_instructionArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__validate_iban",
    "description": "Validate an IBAN format at a mocked level.",
    "parameters": {
      "properties": {
        "iban": {
          "title": "Iban",
          "type": "string"
        },
        "country_code": {
          "title": "Country Code",
          "type": "string"
        }
      },
      "required": [
        "iban",
        "country_code"
      ],
      "title": "validate_ibanArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__get_direct_debits",
    "description": "Return mocked direct debits.",
    "parameters": {
      "properties": {
        "account_id": {
          "title": "Account Id",
          "type": "string"
        }
      },
      "required": [
        "account_id"
      ],
      "title": "get_direct_debitsArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__summarize_cash_flow",
    "description": "Summarize cash flow for a date range.",
    "parameters": {
      "properties": {
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "start_date": {
          "title": "Start Date",
          "type": "string"
        },
        "end_date": {
          "title": "End Date",
          "type": "string"
        }
      },
      "required": [
        "account_id",
        "start_date",
        "end_date"
      ],
      "title": "summarize_cash_flowArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__flag_unusual_spend",
    "description": "Flag unusually high spend.",
    "parameters": {
      "properties": {
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "category": {
          "title": "Category",
          "type": "string"
        },
        "amount": {
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "account_id",
        "category",
        "amount"
      ],
      "title": "flag_unusual_spendArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__get_card_status",
    "description": "Return card status.",
    "parameters": {
      "properties": {
        "card_id": {
          "title": "Card Id",
          "type": "string"
        }
      },
      "required": [
        "card_id"
      ],
      "title": "get_card_statusArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__freeze_card",
    "description": "Mock freezing a card.",
    "parameters": {
      "properties": {
        "card_id": {
          "title": "Card Id",
          "type": "string"
        },
        "reason": {
          "title": "Reason",
          "type": "string"
        }
      },
      "required": [
        "card_id",
        "reason"
      ],
      "title": "freeze_cardArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__calculate_monthly_fees",
    "description": "Calculate mocked monthly account fees.",
    "parameters": {
      "properties": {
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "month": {
          "title": "Month",
          "type": "string"
        }
      },
      "required": [
        "account_id",
        "month"
      ],
      "title": "calculate_monthly_feesArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__check_account_kyc_status",
    "description": "Return KYC status for current account servicing.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        }
      },
      "required": [
        "customer_id"
      ],
      "title": "check_account_kyc_statusArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__get_savings_sweep_recommendation",
    "description": "Recommend a sweep from current account to savings.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "minimum_buffer": {
          "title": "Minimum Buffer",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id",
        "minimum_buffer"
      ],
      "title": "get_savings_sweep_recommendationArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__estimate_foreign_exchange_fee",
    "description": "Estimate FX fee for account transaction.",
    "parameters": {
      "properties": {
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "source_currency": {
          "title": "Source Currency",
          "type": "string"
        },
        "target_currency": {
          "title": "Target Currency",
          "type": "string"
        },
        "amount": {
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "account_id",
        "source_currency",
        "target_currency",
        "amount"
      ],
      "title": "estimate_foreign_exchange_feeArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__get_standing_orders",
    "description": "List mocked standing orders.",
    "parameters": {
      "properties": {
        "account_id": {
          "title": "Account Id",
          "type": "string"
        }
      },
      "required": [
        "account_id"
      ],
      "title": "get_standing_ordersArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__project_end_of_month_balance",
    "description": "Project end-of-month balance.",
    "parameters": {
      "properties": {
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "expected_income": {
          "title": "Expected Income",
          "type": "number"
        },
        "expected_spend": {
          "title": "Expected Spend",
          "type": "number"
        }
      },
      "required": [
        "account_id",
        "expected_income",
        "expected_spend"
      ],
      "title": "project_end_of_month_balanceArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__find_duplicate_charges",
    "description": "Find mocked duplicate charges.",
    "parameters": {
      "properties": {
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "lookback_days": {
          "title": "Lookback Days",
          "type": "integer"
        }
      },
      "required": [
        "account_id",
        "lookback_days"
      ],
      "title": "find_duplicate_chargesArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__get_account_alert_preferences",
    "description": "Return account alert preferences.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        }
      },
      "required": [
        "customer_id",
        "account_id"
      ],
      "title": "get_account_alert_preferencesArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__recommend_fee_waiver",
    "description": "Recommend whether to waive account fees.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "relationship_years": {
          "title": "Relationship Years",
          "type": "integer"
        }
      },
      "required": [
        "customer_id",
        "account_id",
        "relationship_years"
      ],
      "title": "recommend_fee_waiverArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__review_payment_limit",
    "description": "Review payment limit for a current account.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__increase_transfer_limit",
    "description": "Mock increasing transfer limit.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__assess_salary_pattern",
    "description": "Assess salary pattern in current account transactions.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__detect_subscription_spend",
    "description": "Detect recurring subscription spend.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__summarize_merchant_spend",
    "description": "Summarize spend by merchant.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__review_chargeback_case",
    "description": "Review card chargeback case.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__create_card_replacement",
    "description": "Create mocked card replacement order.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__estimate_cash_withdrawal_fee",
    "description": "Estimate cash withdrawal fee.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__review_joint_account_access",
    "description": "Review joint account access status.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__check_sepa_reachability",
    "description": "Check SEPA reachability for a beneficiary.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__validate_payment_reference",
    "description": "Validate payment reference format.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__assess_fraud_alert",
    "description": "Assess mocked fraud alert.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__review_account_closure_readiness",
    "description": "Review account closure readiness.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__calculate_interest_on_positive_balance",
    "description": "Calculate interest on positive balance.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__recommend_budget_category_limit",
    "description": "Recommend budget category limit.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__detect_income_interruption",
    "description": "Detect income interruption risk.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__review_cash_deposit_pattern",
    "description": "Review cash deposit pattern.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__estimate_international_transfer_time",
    "description": "Estimate international transfer time.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__check_beneficiary_risk",
    "description": "Check beneficiary risk score.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__review_power_of_attorney",
    "description": "Review power of attorney on account.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__summarize_monthly_statement",
    "description": "Summarize monthly current account statement.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__detect_round_number_transfers",
    "description": "Detect round-number transfer pattern.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__review_account_package_fit",
    "description": "Review current account package fit.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__estimate_atm_rebate",
    "description": "Estimate ATM fee rebate.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__check_dormancy_risk",
    "description": "Check account dormancy risk.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__review_negative_balance_history",
    "description": "Review negative balance history.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__recommend_alert_threshold",
    "description": "Recommend balance alert threshold.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__assess_travel_notice_need",
    "description": "Assess whether travel notice is needed.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__review_cashback_eligibility",
    "description": "Review cashback eligibility.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  },
  {
    "type": "function",
    "name": "accounts__summarize_account_health",
    "description": "Summarize mocked account health.",
    "parameters": {
      "properties": {
        "customer_id": {
          "title": "Customer Id",
          "type": "string"
        },
        "account_id": {
          "title": "Account Id",
          "type": "string"
        },
        "amount": {
          "default": 1000.0,
          "title": "Amount",
          "type": "number"
        }
      },
      "required": [
        "customer_id",
        "account_id"
      ],
      "title": "toolArguments",
      "type": "object"
    }
  }
]
```
:::

Direct MCP v měření importuje všech 150 tool schemas do modelu. V obou testech je výsledek správný, ale input tokeny jsou vysoké ještě před tím, než agent cokoliv reálně udělá. Máme tady scénář ve kterém je pro správnou odpověď potřeba jen jeden nástroj a jiný, ve kterém jsou potřeba tři. Jsou mezi tím drobné rozdíly dané tím, že provolávání nástroje je output token, který říká co provolat a jaké atributy jak doplnit (proto vyšší počet v druhém případě) a návratové hodnoty z nástrojů jsou input tokeny.

| Scénář | Prompt | Correct | Input | Output | MCP calls | Cena / 1 000 requestů |
|---|---|---:|---:|---:|---:|---:|
| Direct MCP | One loan tool | Yes | 8 148 | 107 | 1 | $6.59 |
| Direct MCP | Three domain tools | Yes | 8 397 | 223 | 3 | $7.30 |

::: callout type="verdict" title="Direct access je jednoduchý, ale drahý baseline"
Výhoda je minimum orchestrace. Nevýhoda je, že model platí za znalost všech nástrojů, i když nakonec použije jeden nebo vůbec žádný.
:::

:::

::: card number="04" title="Tool Search: plné definice až podle potřeby"

Progressive disclosure funguje tak, že model nedostane k dispozici nástroje, ale pouze jeden nástroj na vyhledávání a jeden na exekuci. Implementované to může být různě, ale Foundry používá malý embedding model, takže agent může přirozeným jazykem popsat co potřebuje (například řekne si o "client credit check") a toolbox mu vrátí 1-n nejbližších nástrojů co do významu. Ten potom model pochopí a může zavolat přes `call_tool`.

V cold variantě tedy model vidí jen minimální vstupní sadu.

::: reveal title="Cold Toolbox tools/list"
```json label="measurement/context/cold-toolbox-tools.json"
{
  "tools": [
    {
      "name": "tool_search",
      "description": "Search for relevant tools using keyword search over tool names, titles, and descriptions."
    },
    {
      "name": "call_tool",
      "description": "Invoke a discovered tool by name with arguments."
    }
  ]
}
```
:::

Efekt toho je obrovský. V obou scénářích (říkám jim cold tool, což si vysvětlíme o chvilku později) vidíme zásadní omezení input tokenů.

| Scénář | Prompt | Correct | Input | Output | MCP calls | Cena / 1 000 requestů |
|---|---|---:|---:|---:|---:|---:|
| Cold toolbox + Tool Search | One loan tool | Yes | 2 025 | 175 | 3 | $2.31 |
| Cold toolbox + Tool Search | Three domain tools | Yes | 2 333 | 321 | 6 | $3.20 |

::: callout type="verdict" title="Co se stalo v číslech"
Input šel proti direct MCP dolů zhruba o **75 %** u jednoho toolu a o **72 %** u tří toolů. Output trochu narostl, protože agent dělá více kroků a tool calls, ale cenově to pořád vychází výrazně lépe.
:::

:::

::: card number="05" title="Tool Search s automatickým pinováním"

Toolbox ale dělá ještě jeden zajímavý trik. Postupně se učí, které nástroje jsou nejčastěji používané a ty začne posílat v `tools/list` společně s `call_tool` a `tool_search`. Pokud se tedy trefíme, vidí agent tyto nástroje rovnou a nemusí dělat hledání, volá rovnou. To samozřejmě má potenciál šetřit čas i tokeny, nicméně ne vždy se trefíme. Může to být dobrý kompromis.

Vedle toho je dobré zmínit i ruční pinování. Pokud vím, že některé nástroje jsou pro daného agenta klíčové a chci, aby je měl v kontextu pokaždé, nemusím čekat na automatiku - můžu je pinnut ručně. Auto-pin je adaptivní optimalizace podle používání, manual pin je architektonické rozhodnutí.

Podívejme se na výsledky ve šťastném případě, kdy model dostal všechno rovnou na první, nemusí vůbec nic hledat - negeneruje hledací output tokeny, nenabírá do kontextu výsledky hledání (kdy dostává dle nastavení typicky několik možných shod).

::: reveal title="Warm Toolbox s auto-pin"
```json label="measurement/context/warm-toolbox-tools.json"
{
  "tools": [
    { "name": "tool_search", "meta": { "com.microsoft.foundry/tool_visibility": "system_pinned" } },
    { "name": "call_tool", "meta": { "com.microsoft.foundry/tool_visibility": "system_pinned" } },
    {
      "name": "loans___get_loan_balance",
      "description": "Return current mocked balance for a loan.",
      "meta": { "com.microsoft.foundry/tool_visibility": "auto_pinned" }
    }
  ]
}
```
:::

| Scénář | Prompt | Correct | Input | Output | MCP calls | Cena / 1 000 requestů |
|---|---|---:|---:|---:|---:|---:|
| Warm toolbox + auto-pin | One loan tool | Yes | 565 | 90 | 1 | $0.83 |
| Warm toolbox + auto-pin | Three domain tools | Yes | 874 | 228 | 3 | $1.68 |

::: callout type="verdict" title="Kompromis, který dává smysl"
Warm varianta trochu zvětší viditelný context proti úplně cold režimu, ale pokud se trefí do často používaných tools, zmizí extra search kroky. Výsledek je menší output, méně MCP calls a rychlejší odpověď.
:::

:::

::: card number="06" title="Srovnání variant"

Pojďme si to shrnout a taky přepočítat na ceny za 1000 zavolání. Přímé MCP je drahé, má málo otáček (model nehledá), ale delší kontext zpomaluje první uncached odpověď (pre-fill fáze, čili délka uncached vstupu). Progressive disclosure je o dost levnější, zkracuje pre-fill, ale je tam víc kroků s voláním nástrojů. Pokud se ale trefíme tak, že většina reálných situací bude auto-pinned, máme naprosto ideální situace. Velmi levné, většinou velmi rychlé a přesto schopné naprosto plného řešení s občasným využitím jakéhokoli nástroje v nabídce.

::: tabs id="comparison"

::: tab id="tokens" title="Tokeny a MCP calls"

| Scénář | Prompt | Input | Output | MCP calls |
|---|---|---:|---:|---:|
| Direct MCP | One loan tool | 8 148 | 107 | 1 |
| Cold toolbox + Tool Search | One loan tool | 2 025 | 175 | 3 |
| Warm toolbox + auto-pin | One loan tool | 565 | 90 | 1 |
| Direct MCP | Three domain tools | 8 397 | 223 | 3 |
| Cold toolbox + Tool Search | Three domain tools | 2 333 | 321 | 6 |
| Warm toolbox + auto-pin | Three domain tools | 874 | 228 | 3 |

:::

::: tab id="costs" title="Náklady / 1 000 requestů"

| Scénář | Prompt | Input cost | Output cost | Total |
|---|---|---:|---:|---:|
| Direct MCP | One loan tool | $6.11 | $0.48 | $6.59 |
| Cold toolbox + Tool Search | One loan tool | $1.52 | $0.79 | $2.31 |
| Warm toolbox + auto-pin | One loan tool | $0.42 | $0.41 | $0.83 |
| Direct MCP | Three domain tools | $6.30 | $1.00 | $7.30 |
| Cold toolbox + Tool Search | Three domain tools | $1.75 | $1.44 | $3.20 |
| Warm toolbox + auto-pin | Three domain tools | $0.66 | $1.03 | $1.68 |

:::

:::

::: detail-grid title="Insights" hint="Co z čísel plyne"

::: detail-card title="Input je hlavní problém" summary="Direct MCP posílá plná schémata všech 150 tools."
U direct MCP je output malý, ale input vysoký už na začátku. Tool Search přesune rozhodnutí do runtime: nejdřív hledám capability, potom volám konkrétní tool.
:::

::: detail-card title="Output může narůst" summary="Search znamená víc kroků a víc tool calls."
Cold Tool Search má vyšší output než direct access, protože agent musí hledat a potom volat přes `call_tool`. U modelů, kde je output dražší než input, je potřeba to měřit, ne jen předpokládat.
:::

::: detail-card title="Auto-pin je sweet spot" summary="Časté tools přímo, long-tail přes search."
Warm toolbox nechává v kontextu nejčastější tools a zbytek schovává za vyhledání. V demu to vyšlo nejlépe u tokenů, nákladů i počtu MCP calls.
:::

::: detail-card title="Skills vs. Tool Search" summary="Podobná filozofie, jiná vrstva."
Skills šetří context tím, že dávají agentovi instrukce a postupy až ve chvíli, kdy je potřebuje. Tool Search dělá podobnou věc pro MCP tools: nestrká do promptu všechna schémata, ale odhaluje je postupně.
:::

:::

:::

:::

::: closing
**Progressive disclosure** s Foundry Toolbox snižuje náklady a zvyšuje rychlost vašeho AI agenta.
:::
