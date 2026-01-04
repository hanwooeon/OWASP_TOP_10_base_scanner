import json
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from A07.A07_session_check import Session_Hijacking

class IDAuthFail():
  
  def _init_(self):
    pass
  
  def session_management_run(self, config):
    """A07-01: 세션 관리 취약점 검사"""
    sh = Session_Hijacking()
    return  sh.run(config)
  

if __name__ == "__main__":

  PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  DATA_PATH = os.path.join(PROJECT_ROOT, "etc", "user_info.json")

  with open(DATA_PATH, "r", encoding="utf-8") as f:
      config = json.load(f)


  obj = IDAuthFail()

  result = obj.session_management_run(config)

  with open("./session_hijack_result222222222.json", "w", encoding="utf-8") as f:
      json.dump(result, f, ensure_ascii=False, indent=4)
  