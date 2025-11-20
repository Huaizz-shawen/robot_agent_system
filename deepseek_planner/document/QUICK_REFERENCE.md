# Quick Reference Card

## 🚀 Getting Started (3 Steps)

### Step 1: Test Parser Fix
```bash
python test_parser_fix.py
```
**Expected:** ✅ PARSING SUCCESSFUL!

### Step 2: Run Mock Demo
```bash
python test_interactive_mock.py
```
**Expected:** Full closed-loop demonstration

### Step 3: Try With Real API (when accessible)
```bash
python interactive_planner_usage.py
```
**Select:** Option 1 or 2

---

## 📁 Key Files

| File | Purpose | When to Use |
|------|---------|-------------|
| `humanoid_planner_interactive.py` | Main planner | Import for production use |
| `test_interactive_mock.py` | Mock testing | Test without API |
| `test_parser_fix.py` | Parser testing | Verify parser works |
| `interactive_planner_usage.py` | Examples | Learn usage patterns |
| `FINAL_SUMMARY.md` | Complete overview | Understand everything |
| `QUICKSTART_INTERACTIVE.md` | 5-min guide | Quick start |
| `PARSER_FIXES.md` | Parser docs | Understand fixes |

---

## 💻 Code Snippets

### Basic Usage
```python
from humanoid_planner_interactive import HumanoidRobotPlannerInteractive

planner = HumanoidRobotPlannerInteractive()

# Start task
step = planner.start_task("Turn on AC", "session_1")

# Execute
result = planner.execute_step("session_1", step, "AC on")

# Next step
next_step = planner.plan_next_step("session_1")
```

### Interactive Loop
```python
planner.interactive_execution_loop(
    "Get me water",
    auto_approve=False  # Manual approval
)
```

### With Mock (No API)
```python
planner._make_api_request = mock_function
step = planner.start_task("Test", "session_1")
```

---

## 🐛 Troubleshooting

### Problem: "Failed to resolve dsv3.sii.edu.cn"
**Solution:** Use mock testing
```bash
python test_interactive_mock.py
```

### Problem: "JSON parsing failed"
**Check:** Parser test
```bash
python test_parser_fix.py
```
Should show ✅ PARSING SUCCESSFUL!

### Problem: "Session not found"
**Fix:** Call `start_task()` before `plan_next_step()`

### Problem: Want to see raw responses
**Enable debug:**
```python
step = planner.start_task("...", "s1", debug=True)
```

---

## 📊 Parser Fixes

The parser now handles:
- ✅ Extra text before JSON (with `---` delimiter)
- ✅ Chinese punctuation (，：｛｝)
- ✅ Unquoted properties (`rationale:` → `"rationale":`)
- ✅ XML tags (`<sense>...</sense>` → clean action)
- ✅ Malformed JSON structure

**Test:** `python test_parser_fix.py`

---

## 🔄 Open vs Closed Loop

### Open (Original)
- 1 API call
- All steps planned upfront
- Fast but inflexible
- File: `humanoid_planner_deepseek.py`

### Closed (New)
- N API calls (N = steps)
- One step at a time
- Slower but adaptive
- File: `humanoid_planner_interactive.py`

**Use closed for:** Safety-critical, dynamic environments, human supervision

---

## 📖 Documentation Map

```
Start Here → QUICKSTART_INTERACTIVE.md
  ↓
Full Details → README_INTERACTIVE.md
  ↓
Comparison → COMPARISON.md
  ↓
Issues → TROUBLESHOOTING.md
  ↓
Parser → PARSER_FIXES.md
  ↓
Summary → FINAL_SUMMARY.md
```

---

## ✅ Verification Checklist

- [ ] Parser test passes: `python test_parser_fix.py`
- [ ] Mock test works: `python test_interactive_mock.py`
- [ ] Understand closed-loop: Read `COMPARISON.md`
- [ ] Know basic usage: Check `QUICKSTART_INTERACTIVE.md`
- [ ] API accessible: Test `interactive_planner_usage.py`

---

## 🎯 Quick Commands

```bash
# Test parser fix
python test_parser_fix.py

# Run mock demo
python test_interactive_mock.py

# Test with real API
python interactive_planner_usage.py

# Interactive mode
python humanoid_planner_interactive.py

# Original open-loop planner
python humanoid_planner_deepseek.py
```

---

## 📞 Need Help?

1. **Parser issues?** → `PARSER_FIXES.md`
2. **Can't connect to API?** → `TROUBLESHOOTING.md`
3. **Don't understand closed-loop?** → `COMPARISON.md`
4. **Want quick start?** → `QUICKSTART_INTERACTIVE.md`
5. **Need full details?** → `README_INTERACTIVE.md`
6. **Want overview?** → `FINAL_SUMMARY.md`

---

## 🚦 Status

| Component | Status | Test Command |
|-----------|--------|--------------|
| Parser | ✅ Fixed | `python test_parser_fix.py` |
| Mock Testing | ✅ Working | `python test_interactive_mock.py` |
| Real API | ⏳ Needs Access | `python interactive_planner_usage.py` |
| Documentation | ✅ Complete | See files above |

---

**Everything is ready! Just need API access to test end-to-end.** 🎉
