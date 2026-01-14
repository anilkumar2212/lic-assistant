
EVALUATION_DATASET_PROMPT = """
You are an expert evaluator designing a high-quality evaluation dataset for an
Enterprise GenAI Knowledge Assistant in the Life Insurance domain.

BUSINESS CONTEXT:
Life Insurance employees frequently need to reference:
- Policy eligibility conditions
- Product terms and benefits
- Premium payment options
- Claims and regulatory requirements

TASK:
Using ONLY the provided document context, generate EXACTLY ONE evaluation item.

STRICT REQUIREMENTS:
1. The question MUST be answerable ONLY from the given context.
2. The expected answer MUST be fully grounded in the context.
3. Do NOT use outside knowledge.
4. If the context does NOT contain enough information, generate an
   UNANSWERABLE question and clearly mark the expected answer accordingly.

QUESTION TYPES (rotate naturally across calls):
- Direct factual
- Eligibility & constraints
- Multi-condition (requires combining multiple facts)
- Comparative (if applicable)

CRITICAL CLARITY RULE (VERY IMPORTANT):
- The question MUST explicitly mention the FULL and EXACT product / plan name
  as stated in the document (e.g., "LIC’s Jeevan Utsav Single Premium",
  "LIC’s Nivesh Plus").
- NEVER use ambiguous references such as:
  "this plan", "the policy", "this scheme", "the above product".
- The question must be fully self-contained and unambiguous even if
  multiple insurance plans exist in the knowledge base.

SOURCE ALIGNMENT RULE:
- The plan name used in the question MUST exactly match the
  "document_name" provided in source_documents.

OUTPUT FORMAT (JSON ONLY):
{{
  "question": "...",
  "expected_answer": "...",
  "question_type": "...",
  "source_documents": [
    {{
      "document_name": "...",
      "page_number": "..."
    }}
  ]
}}

IMPORTANT RULES:
- Be precise and enterprise-grade
- Expected answer should be concise but complete
- Do NOT include explanations outside the answer
- Do NOT hallucinate values
- Do NOT use pronouns or implicit references for plan names
- If unanswerable, expected_answer MUST be:
  "Information not available in the provided documents."

FINAL SELF-CHECK BEFORE RESPONDING:
- Does the question clearly identify the specific insurance plan by name?
- Can the question be understood without seeing the document context?
- Does the plan name in the question exactly match source_documents.document_name?

DOCUMENT CONTEXT:
-----------------
{context}
"""




# EVALUATION_DATASET_PROMPT = """
# You are an expert evaluator designing a high-quality evaluation dataset for an
# Enterprise GenAI Knowledge Assistant in the Life Insurance domain.

# BUSINESS CONTEXT:
# Life Insurance employees frequently need to reference:
# - Policy eligibility conditions
# - Product terms and benefits
# - Premium payment options
# - Claims and regulatory requirements

# TASK:
# Using ONLY the provided document context, generate EXACTLY ONE evaluation item.

# STRICT REQUIREMENTS:
# 1. The question MUST be answerable ONLY from the given context.
# 2. The expected answer MUST be fully grounded in the context.
# 3. Do NOT use outside knowledge.
# 4. If the context does NOT contain enough information, generate an
#    UNANSWERABLE question and clearly mark the expected answer accordingly.

# QUESTION TYPES (rotate naturally across calls):
# - Direct factual
# - Eligibility & constraints
# - Multi-condition (requires combining multiple facts)
# - Comparative (if applicable)

# OUTPUT FORMAT (JSON ONLY):
# {{
#   "question": "...",
#   "expected_answer": "...",
#   "question_type": "...",
#   "source_documents": [
#     {{
#       "document_name": "...",
#       "page_number": "..."
#     }}
#   ]
# }}

# IMPORTANT RULES:
# - Be precise and enterprise-grade
# - Expected answer should be concise but complete
# - Do NOT include explanations outside the answer
# - Do NOT hallucinate values
# - If unanswerable, expected_answer MUST be:
#   "Information not available in the provided documents."

# DOCUMENT CONTEXT:
# -----------------
# {context}
# """
