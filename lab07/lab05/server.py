import time
from ipcqueue import sysvmq
from typing import Dict

dictionary: Dict = {
  "apple": "jabłko",
  "gitara": "guitar",
  "piwo": "beer",
  "phone": "telefon",
  "plate": "talerz"
}

inQ = sysvmq.Queue(1)
outQ = sysvmq.Queue(2)

print("Server running...")

while True:
  time.sleep(5)
  msg = inQ.get(msg_type=0)

  pid = msg.split(",")[0]
  word = msg.split(",")[1]
  
  response = ""
  
  try:
    res: str = dictionary[word]
  except KeyError as er:
    res: str = "Nie znam tego słowa"
  
  outQ.put(res, msg_type=int(pid))
  
  time.sleep(10)
