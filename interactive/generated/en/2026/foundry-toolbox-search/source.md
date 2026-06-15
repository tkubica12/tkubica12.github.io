---
format_version: 1
title: "Cheaper and faster agents with progressive disclosure MCP through Foundry Toolbox Search"
eyebrow: "Tool Search, auto-pin, and fewer input tokens"
subtitle: "Foundry Toolbox unifies many MCP servers into one endpoint. Tool Search adds progressive disclosure: the agent first sees only a minimum set of tools and retrieves full definitions only when it really needs them."
slug: foundry-toolbox-search
date: 2026-06-09
language: en
source_language: cs-CZ
source_slug: foundry-toolbox-search
translation: machine
translated_from_hash: b6cf4c9ec39f63038337faf89a15f4503641d175fa3a98784f3d2419c71ac8a4
translation_status: current
status: published
published: true
canonical_url: "/en/2026/foundry-toolbox-search/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
design:
  theme: simple-neutral
  density: presentation
---

# Cheaper and faster agents with progressive disclosure MCP through Foundry Toolbox Search

My tests and results are in the [tkubica12/foundry-toolbox-search](https://github.com/tkubica12/foundry-toolbox-search) repository.

::: group id="chapters" title="From MCP schemas to token savings"

::: card number="01" title="MCP definitions and the input token explosion" default="open"

MCP works by sending the agent - more precisely, the system harness or MCP client - a list of all tools, descriptions of what they are for and how to use them, and also any input attributes and their explanations. The whole thing can look something like this.

::: reveal title="Standard MCP tools/list - JSON example"
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

In the demo there are three separate MCP servers for FSI domains: `loans`, `investments`, and `accounts`. Raw `tools/list` from these servers is stored in [`standalone-mcp-tools.json`](https://github.com/tkubica12/foundry-toolbox-search/blob/main/measurement/context/standalone-mcp-tools.json).

It looks innocent, but there are two practical problems right away.

::: tabs id="mcp-problems"

::: tab id="tokens" title="Tokens"
**Tool definitions take up a lot of room in context.**

The first problem is, of course, that this is really a lot of text, and it goes into input tokens regardless of which tool the agent actually uses, and even if it decides not to use any tool at all. So the user's:

```text label="Uživatel"
Ahoj
```

and the answer:

```text label="Agent"
Ahoj, co pro tebe můžu udělat?
```

can still mean thousands of input tokens, their cost, and a longer time to first token.
:::

::: tab id="endpoint-management" title="Endpoint management"
**Different MCP servers have different URLs, access models, and catalogs.**

The second problem is that there may be several MCP servers, with different URLs, access, and catalogs, and it makes sense to unify this. Ideally, you create a toolbox that contains the right MCP servers for the task.
:::

:::

::: callout type="verdict" title="Foundry"
Foundry Toolbox helps with both problems, so let us look at it.
:::

:::

::: card number="02" title="Foundry Toolbox"

Foundry is a Microsoft platform for standardized, open creation of agentic solutions, chatbots, or AI workflows and routines. It brings an agent runtime, sandboxed hosting for third-party runtimes, models, observability, guardrails, evaluations, red teaming, memory, tools, and much more. In this article I will focus on tools, specifically Foundry Toolbox and Tool Search.

::: steps title="Mental model"
1. **MCP servers** - individual domain capabilities, often with many tools.
2. **Foundry Toolbox** - a catalog and one MCP endpoint over those capabilities.
3. **Tool Search** - a small input set of tools (`tool_search`, `call_tool`) and retrieval of full definitions only when needed.
4. **Auto-pin** - frequently used tools appear directly in context after warm-up.
:::

In the Build section of the Foundry portal, we can look at Tools, where individual tools live, as do Skills and the Toolboxes mentioned above.

![Foundry Tools in the Build section](/images/2026/ZoomIt%202026-06-08%20130657.png)

I can select tools from the catalog.

![Tool catalog in Foundry](/images/2026/ZoomIt%202026-06-08%20130955.png)

Or I can use a custom API call, A2A (communication to another agent as a tool), or MCP, which was my case.

![Custom tools, A2A, and MCP](/images/2026/ZoomIt%202026-06-08%20131121.png)

I used three MCP servers that I deployed to Azure Container Apps. They represent banking areas, specifically accounts, investments, and loans, and they return mocked responses for demo purposes. For example, for loans I have calls such as `get_mortgage_affordability`, `quote_personal_loan`, or `check_loan_eligibility`.

I connected these three servers, each containing 50 tools, into a toolbox. Notice an important point - I can associate a guardrails policy. That can be useful, for example, for watching PII information or jailbreak attempts, especially if I use A2A for agent-as-tool scenarios.

![Toolbox with three MCP servers and a guardrails policy](/images/2026/ZoomIt%202026-06-08%20131501.png)

I can connect this toolbox, for example, to a Foundry Prompt agent, Microsoft Agent Framework, or LangGraph.

![Using a toolbox in agent runtimes](/images/2026/ZoomIt%202026-06-08%20132003.png)

According to the documentation, [Foundry Toolbox](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/toolbox) is a curated bundle of tools that you configure once and expose as one MCP-compatible endpoint. The toolbox can include MCP servers, APIs, A2A, Foundry tools, and other capabilities. In practice, it is a single place where you assemble what the agent should be able to use.

::: callout type="rule" title="It is not just convenience"
One URL for the agent is nice. But the more interesting part is control over **what gets into model context** and what stays hidden behind search.
:::

:::

::: card number="03" title="Full tool definitions: direct access scenario"

The first scenario assumes a classic MCP solution: full definitions of all calls, their descriptions, and attributes. From a token perspective, it does not really matter whether these are separate MCP servers or whether we unify them in a toolbox; the result is the same. If you want, look at what the model sees.

::: reveal title="What the model sees with direct access"
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

Direct MCP in the measurement imports all 150 tool schemas into the model. In both tests the result is correct, but input tokens are high before the agent actually does anything. We have one scenario where only one tool is needed for the correct answer and another where three tools from different domains are needed.

| Scenario | Prompt | Correct | Input | Output | MCP calls | Cost / 1,000 requests |
|---|---|---:|---:|---:|---:|---:|
| Direct MCP | One loan tool | Yes | 8 148 | 107 | 1 | $6.59 |
| Direct MCP | Three domain tools | Yes | 8 397 | 223 | 3 | $7.30 |

::: callout type="verdict" title="Direct access is a simple but expensive baseline"
The advantage is minimal orchestration. The disadvantage is that the model pays for knowing all tools, even if it ultimately uses one or none at all.
:::

:::

::: card number="04" title="Tool Search: full definitions only when needed"

Progressive disclosure works by not giving the model the tools themselves, but only one tool for search and one for execution. It can be implemented in different ways, but Foundry uses a small embedding model, so the agent can describe in natural language what it needs, find relevant tools, and then call the selected one.

In the cold variant, the model sees only the minimal input set.

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

The effect is huge. In both scenarios (I call them cold tool, which I will explain in a moment) we see a major reduction in input tokens.

| Scenario | Prompt | Correct | Input | Output | MCP calls | Cost / 1,000 requests |
|---|---|---:|---:|---:|---:|---:|
| Cold toolbox + Tool Search | One loan tool | Yes | 2 025 | 175 | 3 | $2.31 |
| Cold toolbox + Tool Search | Three domain tools | Yes | 2 333 | 321 | 6 | $3.20 |

::: callout type="verdict" title="What happened in the numbers"
Input went down compared with direct MCP by roughly **75%** for one tool and **72%** for three tools. Output grew a little, because the agent performs more steps and tool calls, but the total cost is still much better.
:::

:::

::: card number="05" title="Tool Search with automatic pinning"

Toolbox does one more interesting trick. It gradually learns which tools are used most often and starts sending them in `tools/list` together with `call_tool` and `tool_search`. If we hit the right tools, the agent sees them immediately and does not need to search; it calls them directly.

It is also worth mentioning manual pinning. If I know that some tools are critical for a given agent and I want them in context every time, I do not have to wait for automation - I can pin them manually. Auto-pin is adaptive optimization based on usage; manual pin is an explicit architecture decision.

Let us look at the results in the happy path, where the model got everything right away on the first try, does not have to search at all, does not generate search output tokens, and does not add search results into context (where it typically receives several possible matches depending on settings).

::: reveal title="Warm Toolbox with auto-pin"
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

| Scenario | Prompt | Correct | Input | Output | MCP calls | Cost / 1,000 requests |
|---|---|---:|---:|---:|---:|---:|
| Warm toolbox + auto-pin | One loan tool | Yes | 565 | 90 | 1 | $0.83 |
| Warm toolbox + auto-pin | Three domain tools | Yes | 874 | 228 | 3 | $1.68 |

::: callout type="verdict" title="A compromise that makes sense"
The warm variant makes the visible context a little larger than the fully cold mode, but if it hits the frequently used tools, the extra search steps disappear. The result is lower output, fewer MCP calls, and a faster answer.
:::

:::

::: card number="06" title="Comparing the variants"

Let us summarize it and also recalculate the costs for 1,000 calls. Direct MCP is expensive, has fewer moving parts (the model does not search), but the longer context slows down the first uncached answer (the pre-fill phase, meaning the length of uncached input). Progressive disclosure is much cheaper, shortens the initial context, but adds some orchestration and tool calls.

::: tabs id="comparison"

::: tab id="tokens" title="Tokens and MCP calls"

| Scenario | Prompt | Input | Output | MCP calls |
|---|---|---:|---:|---:|
| Direct MCP | One loan tool | 8 148 | 107 | 1 |
| Cold toolbox + Tool Search | One loan tool | 2 025 | 175 | 3 |
| Warm toolbox + auto-pin | One loan tool | 565 | 90 | 1 |
| Direct MCP | Three domain tools | 8 397 | 223 | 3 |
| Cold toolbox + Tool Search | Three domain tools | 2 333 | 321 | 6 |
| Warm toolbox + auto-pin | Three domain tools | 874 | 228 | 3 |

:::

::: tab id="costs" title="Cost / 1,000 requests"

| Scenario | Prompt | Input cost | Output cost | Total |
|---|---|---:|---:|---:|
| Direct MCP | One loan tool | $6.11 | $0.48 | $6.59 |
| Cold toolbox + Tool Search | One loan tool | $1.52 | $0.79 | $2.31 |
| Warm toolbox + auto-pin | One loan tool | $0.42 | $0.41 | $0.83 |
| Direct MCP | Three domain tools | $6.30 | $1.00 | $7.30 |
| Cold toolbox + Tool Search | Three domain tools | $1.75 | $1.44 | $3.20 |
| Warm toolbox + auto-pin | Three domain tools | $0.66 | $1.03 | $1.68 |

:::

:::

::: detail-grid title="Insights" hint="What follows from the numbers"

::: detail-card title="Input is the main problem" summary="Direct MCP sends full schemas for all 150 tools."
With direct MCP, output is small, but input is high from the start. Tool Search moves the decision into runtime: first I search for a capability, then I call a specific tool.
:::

::: detail-card title="Output can grow" summary="Search means more steps and more tool calls."
Cold Tool Search has higher output than direct access, because the agent has to search and then call through `call_tool`. With models where output is more expensive than input, you need to measure it, not just assume.
:::

::: detail-card title="Auto-pin is the sweet spot" summary="Frequent tools directly, long-tail through search."
Warm toolbox keeps the most frequent tools in context and hides the rest behind search. In the demo it came out best for tokens, cost, and number of MCP calls.
:::

::: detail-card title="Skills vs. Tool Search" summary="A similar philosophy, a different layer."
Skills save context by giving the agent instructions and procedures only when it needs them. Tool Search does a similar thing for MCP tools: it does not put all schemas into the prompt, but reveals them progressively.
:::

:::

:::

:::

::: closing
**Progressive disclosure** with Foundry Toolbox lowers costs and increases the speed of your AI agent.
:::
