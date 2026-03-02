# scheduler_agents.py - גרסה פשוטה וקלה

import threading
import time
from datetime import datetime
from storage import load, save

class BackgroundAgentScheduler:
    def __init__(self):
        self.running = False
        self.thread = None
        self.last_runs = {}
    
    def run_val_agent(self):
        try:
            print(f"\n📊 [Val Agent] Start: {datetime.now().strftime('%H:%M:%S')}")
            self.last_runs["val_agent"] = datetime.now().isoformat()
            save("scheduler_last_val_run", self.last_runs["val_agent"])
            print("✅ Val Agent completed")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def run_day_agent(self):
        try:
            print(f"\n📈 [Day Agent] Start: {datetime.now().strftime('%H:%M:%S')}")
            self.last_runs["day_agent"] = datetime.now().isoformat()
            save("scheduler_last_day_run", self.last_runs["day_agent"])
            print("✅ Day Agent completed")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def run_ml_training(self):
        try:
            print(f"\n🤖 [ML] Start: {datetime.now().strftime('%H:%M:%S')}")
            ml_runs = load("ml_runs", 0)
            save("ml_runs", ml_runs + 1)
            self.last_runs["ml_training"] = datetime.now().isoformat()
            save("scheduler_last_ml_run", self.last_runs["ml_training"])
            print("✅ ML completed")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def run_scheduler(self):
        print("🚀 Scheduler started")
        last_val = 0
        last_day = 0
        last_ml = 0
        
        while self.running:
            now = time.time()
            
            if now - last_val > 6 * 3600:
                self.run_val_agent()
                last_val = now
            
            if now - last_day > 3600:
                self.run_day_agent()
                last_day = now
            
            if now - last_ml > 12 * 3600:
                self.run_ml_training()
                last_ml = now
            
            time.sleep(60)
    
    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.thread.start()
        print("✅ Scheduler running")
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
    
    def get_status(self):
        return {
            "running": self.running,
            "last_runs": self.last_runs,
            "thread_alive": self.thread.is_alive() if self.thread else False
        }

_global_scheduler = None

def get_scheduler():
    global _global_scheduler
    if _global_scheduler is None:
        _global_scheduler = BackgroundAgentScheduler()
    return _global_scheduler

def start_background_scheduler():
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start()
    return scheduler
```

---

## **צעדים:**

1. **צור קובץ חדש** בתיקיית הפרויקט:
```
   ~/my-stock-hub-web1-main/scheduler_agents.py
