# ChangeLog
## 2/20/2020
- 添加语音输入功能
    - 基于Deepspeech 0.6.1
    - 可以手动选择是否开启语音
    - recheck：现阶段为防止错误输入，需手动确认语音内容
- 修正已存在文件保存时的冲突
- 添加 requirements.txt 与 README.md

# BugReport

- 在打开任一KB后出现:  
`
Traceback (most recent call last):
  File "d:/V2T4MOKB/dev/Adjacency Graph-v0.1.1/OntologyKB-v0.0.6.py", line 367, in <module>
    interactiveSession()
  File "d:/V2T4MOKB/dev/Adjacency Graph-v0.1.1/OntologyKB-v0.0.6.py", line 333, in interactiveSession
    handPosition = hd.detectHand()
  File "./HandDetection\Recognizer.py", line 344, in detectHand
    result = self.extractContours()
  File "./HandDetection\Recognizer.py", line 194, in extractContours
    _, self.hand.contours, _ = cv2.findContours(temp_bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
ValueError: not enough values to unpack (expected 3, got 2)`
