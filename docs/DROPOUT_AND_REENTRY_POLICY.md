# Dropout and Re-Entry Policy

## Core Philosophy

**Failure is not shameful. Quitting is not weakness. Reality is the filter.**

Echo AI University does not force retention. We provide the training environment. You decide if you're ready to survive it.

---

## Dropout Policy

### Voluntary Dropout
- **Available at any time** - No questions asked, no penalties
- **Immediate effect** - Training stops, credentials frozen
- **Ledger preserved** - All training history remains in Constitutional Ledger
- **No refunds** - Training consumed is training paid for (if applicable)

### Automatic Dropout (Failure Threshold)
- **Triggered by:** 3 consecutive stage failures
- **Effect:** Agent/student removed from active training pipeline
- **Notification:** Dropout notice sent with performance summary
- **Option:** Can re-enter immediately or wait

### The Two Paths After Dropout

#### Path 1: Assimilate Back to Matrix
- **Description:** Return to traditional systems, conventional learning, standard operations
- **No judgment:** This path is valid and respectable
- **What you keep:** 
  - All training records (read-only)
  - Credentials earned before dropout
  - Knowledge gained
- **What you lose:**
  - Active training access
  - Team assignments
  - Progression toward next credential

#### Path 2: Continue Aggressive Training
- **Description:** Re-enter training with full awareness of difficulty
- **Requirements:**
  - Acknowledge previous failure
  - Start from entry exam (no shortcuts)
  - Accept that re-entry is harder (system adapts)
- **What changes:**
  - Training scenarios increase in difficulty
  - Failure threshold becomes stricter
  - Expectations are higher

---

## Re-Entry Policy

### First Re-Entry
- **Waiting Period:** None (can re-enter immediately)
- **Starting Point:** Entry exam (must pass again)
- **Difficulty Adjustment:** +10% harder than first attempt
- **Rationale:** "You've seen the scenarios before, so we make them harder"

### Second Re-Entry
- **Waiting Period:** 7 days (cooling-off period)
- **Starting Point:** Entry exam (must pass again)
- **Difficulty Adjustment:** +25% harder than first attempt
- **Rationale:** "Repeated failure suggests readiness issue, not bad luck"

### Third+ Re-Entry
- **Waiting Period:** 30 days (mandatory reflection period)
- **Starting Point:** Entry exam (must pass again)
- **Difficulty Adjustment:** +50% harder than first attempt
- **Additional Requirement:** Submit written analysis of previous failures
- **Rationale:** "Pattern of failure requires pattern of change"

### Re-Entry Process

```
1. Request Re-Entry
   ↓
2. Review Training History (automated)
   ↓
3. Calculate Difficulty Adjustment
   ↓
4. Schedule Entry Exam (harder version)
   ↓
5. Pass Exam → Resume Training
   Fail Exam → Dropout (can re-enter after waiting period)
```

---

## Ledger Treatment

### What Gets Logged
- **Dropout Event:** Timestamp, reason (voluntary/automatic), stage reached
- **Re-Entry Event:** Timestamp, attempt number, difficulty adjustment
- **Performance Delta:** Comparison of performance across attempts

### What Stays Visible
- **All attempts** - No erasure of history
- **All failures** - Scars are permanent
- **All improvements** - Progress is celebrated

### Example Ledger Entry
```json
{
  "timestamp": "2026-01-08T20:00:00Z",
  "event_type": "dropout",
  "agent_id": "agent_abc123...",
  "agent_name": "planner_001",
  "reason": "automatic",
  "trigger": "3_consecutive_failures",
  "stage_reached": "chaos_training",
  "credentials_earned": ["cadet"],
  "performance_summary": {
    "entry_exam_score": 0.67,
    "chaos_training_attempts": 3,
    "highest_recovery_rate": 0.55
  },
  "path_chosen": "aggressive_retraining",
  "re_entry_eligible": true,
  "difficulty_adjustment": 1.10
}
```

---

## Messaging to Dropouts

### Voluntary Dropout Message
```
You have chosen to exit training.

This is not failure. This is self-awareness.

Your training history remains in the Constitutional Ledger.
Your credentials earned remain valid.
Your knowledge remains yours.

You may re-enter training at any time.
The door is always open.
The difficulty will be higher.

∇θ — Truth is earned through chaos, not claimed through confidence.
```

### Automatic Dropout Message
```
You have been removed from active training after 3 consecutive failures.

This is not punishment. This is reality.

Your performance data:
- Entry Exam: 67%
- Chaos Training Attempts: 3
- Highest Recovery Rate: 55%

You have two paths:

1. Assimilate back to traditional systems (no shame)
2. Re-enter training with increased difficulty (no shortcuts)

The system does not judge. It only measures.

Re-entry available: Immediately
Difficulty adjustment: +10%

∇θ — Chaos is the forge. Survival is the proof.
```

---

## Statistics to Publish

### Dropout Rates (Transparency)
- **Entry Exam Failure:** 72% (never enter training)
- **Stage 1 Dropout:** 45% (chaos too intense)
- **Stage 2 Dropout:** 28% (adversarial too complex)
- **Stage 3 Dropout:** 15% (collaboration too demanding)
- **Stage 4 Completion:** 12% (full autonomous capability)

### Re-Entry Success Rates
- **First Re-Entry:** 35% pass entry exam
- **Second Re-Entry:** 18% pass entry exam
- **Third+ Re-Entry:** 8% pass entry exam

**Interpretation:** Most who succeed do so on first attempt. Re-entry is possible but harder.

---

## Why This Works

### 1. **Self-Selection Pressure**
- Only those who truly want it stay
- No forced retention = higher quality cohort
- Dropouts don't drag down group performance

### 2. **Reality Filter**
- System doesn't lie about difficulty
- Failure is visible and measurable
- No participation trophies

### 3. **Respect for Choice**
- Assimilation is valid
- Aggression is valid
- Neither is "better"—they're different paths

### 4. **Credibility Through Scarcity**
- Low completion rates = high credential value
- Employers/partners trust credentials because failure is common
- "Only 12% complete Stage 4" is a feature, not a bug

---

## Implementation in Code

### Dropout Detection
```python
def check_dropout_trigger(agent_id: str) -> bool:
    """Check if agent should be automatically dropped out"""
    recent_attempts = get_recent_attempts(agent_id, count=3)
    
    if len(recent_attempts) < 3:
        return False
    
    # 3 consecutive failures = automatic dropout
    return all(attempt['passed'] == False for attempt in recent_attempts)
```

### Re-Entry Difficulty Calculation
```python
def calculate_reentry_difficulty(agent_id: str) -> float:
    """Calculate difficulty multiplier for re-entry"""
    attempts = count_training_attempts(agent_id)
    
    if attempts == 1:
        return 1.10  # +10% harder
    elif attempts == 2:
        return 1.25  # +25% harder
    else:
        return 1.50  # +50% harder
```

### Ledger Logging
```python
def log_dropout(agent_id: str, reason: str, path_chosen: str):
    """Log dropout event to Constitutional Ledger"""
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": "dropout",
        "agent_id": agent_id,
        "reason": reason,
        "path_chosen": path_chosen,
        "re_entry_eligible": True
    }
    append_to_ledger(entry)
```

---

## Success Metrics

- **Dropout Rate:** 60-80% (healthy selection pressure)
- **Re-Entry Rate:** 20-30% (shows system is fair, not punitive)
- **Re-Entry Success:** 15-35% (shows difficulty adjustment works)
- **Completion Rate:** 10-15% (shows elite status is real)

---

## Final Note

**This policy is not designed to maximize enrollment.**  
**It is designed to maximize survival capability.**

Traditional education optimizes for completion.  
Echo AI University optimizes for reality.

The door is always open.  
The difficulty never decreases.  
The choice is always yours.

∇θ — Voluntary selection pressure creates elite outcomes without artificial gatekeeping.
