---
name: ai-content-automation-tts
description: TTS文本转语音模块。支持多音色、多语言配音，自动匹配视频时间轴。
---

# TTS配音模块

## 功能

- 文本转语音（edge-tts 免费方案）
- 多音色选择（中英文多种声音）
- 自动生成时间轴（SRT字幕）
- 音频与视频同步

## 使用方式

```bash
# 生成配音
python -m tts_engine --script script.md --output ./audio --voice zh-CN-XiaoxiaoNeural

# 生成配音+字幕
python -m tts_engine --script script.md --output ./audio --srt

# 使用自定义音色
python -m tts_engine --script script.md --voice zh-CN-YunxiNeural
```

## 可用音色

| 音色ID | 名称 | 适用场景 |
|--------|------|----------|
| zh-CN-XiaoxiaoNeural | 晓晓 | 通用女声 |
| zh-CN-YunxiNeural | 云希 | 通用男声 |
| zh-CN-XiaoyiNeural | 晓伊 | 活泼女声 |
| zh-CN-YunyangNeural | 云扬 | 专业男声 |
| en-US-JennyNeural | Jenny | 英文女声 |
| en-US-GuyNeural | Guy | 英文男声 |

## 输出文件

```
audio/
├── segment_001.mp3
├── segment_001.srt
├── segment_002.mp3
├── segment_002.srt
└── timeline.json    # 时间轴信息
```

## 时间轴格式

```json
{
  "segments": [
    {
      "id": 1,
      "text": "文本内容",
      "start": 0.0,
      "end": 3.5,
      "audio_file": "segment_001.mp3",
      "srt_file": "segment_001.srt"
    }
  ],
  "total_duration": 180.5
}
```

## 依赖

- edge-tts（免费）
- azure-cognitiveservices-speech（可选，需要key）
- tqdm（进度条）
