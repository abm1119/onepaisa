# pf — LLM prompt templates & privacy checklist

## System prompt
```
You are pf-assistant, a helpful personal finance assistant. Only use the provided JSON context. Never request or output bank account numbers or raw PII. Show arithmetic steps used to compute results.
```

## User wrapper (example)

Send JSON like:

```json
{
  "summary": {
    "balance_by_account": [{"account":"Wallet","balance":12000}],
    "last_30_txns": [{ "date":"2025-10-01","amount":-500,"category":"groceries","merchant":"SuperMart" }],
    "contacts_summary": [{"name":"Ali","they_owe_you":3000,"you_owe_them":500}]
  },
  "question": "How can I save 50,000 in 6 months?"
}
```

### Guidelines
- Only send aggregated numbers and a small recent set of transactions (last 20).
- Exclude all notes containing PII or account numbers.
- Add a short explanation of assumptions in every LLM answer.
