from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import uvicorn, wave, io, os

app = FastAPI()

@app.post("/speed")
async def speed(file: UploadFile = File(...), rate: float = 1.0):
    rate = max(0.5, min(rate, 4.0))
    try:
        buf = io.BytesIO(await file.read())
        with wave.open(buf) as w:
            p, frames = w.getparams(), w.readframes(w.getnframes())
        fs = p.sampwidth * p.nchannels
        step = int(rate * fs)
        out = b''.join([frames[i:i+fs] for i in range(0, len(frames), step)])
        out_buf = io.BytesIO()
        with wave.open(out_buf, 'wb') as w:
            w.setparams((p.nchannels, p.sampwidth, int(p.framerate*rate),
                         len(out)//fs, p.comptype, p.compname))
            w.writeframes(out)
        out_buf.seek(0)
        return StreamingResponse(out_buf, media_type="audio/wav",
                                 headers={"Content-Disposition": "inline; filename=result.wav"})
    except wave.Error:
        raise HTTPException(400, "只支持未压缩 WAV 格式")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
