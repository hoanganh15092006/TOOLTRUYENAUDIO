# ĐỀ XUẤT NÂNG CẤP (PROPOSAL): TÍCH HỢP MASTERING EBU R128 (-16 LUFS) VÀO AUDIO MIXER

- **Mã đề xuất:** `PROP-AUDIO-20261021-01`
- **Mục tiêu:** Tự động chuẩn hóa âm lượng chuẩn EBU R128 (-16.0 LUFS, True Peak <= -1.5 dBTP) trực tiếp trong quá trình mix voiceover và BGM, loại bỏ hoàn toàn hiện tượng lệch âm lượng giữa các đoạn trong truyện dài >20 phút.
- **Trạng thái:** `[PENDING]` (Chờ người dùng xác nhận "Duyệt" / "Merge")

---

## 1. Vấn đề Phát Hiện Thực Tế
Hiện tại trong `src/tts_engine/audio_mixer.py`, filter complex sử dụng `amix=inputs=2:duration=first:dropout_transition=2` đơn thuần. Với các tập truyện dài (>20 phút), giọng đọc từ các chunk khác nhau có thể có biên độ chênh lệch, và khi phối cùng BGM chưa có bước mastering tổng thể, âm lượng tích hợp có thể dao động từ -12 LUFS đến -22 LUFS gây mỏi tai người nghe.

---

## 2. Giải Pháp Đề Xuất
Tích hợp bộ lọc `loudnorm=I=-16:TP=-1.5:LRA=11` vào chuỗi filter audio của FFmpeg và thêm phương thức `apply_mastering` chuyên biệt.

### Bản Diff Đề Xuất cho `src/tts_engine/audio_mixer.py`:

```diff
--- a/src/tts_engine/audio_mixer.py
+++ b/src/tts_engine/audio_mixer.py
@@ -20,9 +20,10 @@ class AudioMixer:
     """
 
-    def __init__(self, bgm_dir: str = "assets/bgm", default_bgm_volume_db: float = -24.0):
+    def __init__(self, bgm_dir: str = "assets/bgm", default_bgm_volume_db: float = -24.0, target_lufs: float = -16.0):
         self.bgm_dir = bgm_dir
         self.default_bgm_volume_db = default_bgm_volume_db
+        self.target_lufs = target_lufs
 
     def find_bgm_track(self, explicit_path: Optional[str] = None) -> Optional[str]:
@@ -101,7 +102,7 @@ class AudioMixer:
         # Looping BGM and mix with speech
         filter_complex = (
             f"[1:a]volume={volume_db}dB[bgm_ducked];"
-            f"[0:a][bgm_ducked]amix=inputs=2:duration=first:dropout_transition=2[out]"
+            f"[0:a][bgm_ducked]amix=inputs=2:duration=first:dropout_transition=2,loudnorm=I={self.target_lufs}:TP=-1.5:LRA=11[out]"
         )
```

---

## 3. Kế Hoạch Kiểm Thử Hồi Quy
- Chạy lại toàn bộ `python -m unittest discover tests`.
- Kiểm định file test audio xuất ra bằng `audio_director.py audit` để xác nhận đạt điểm `>= 90/100`.
