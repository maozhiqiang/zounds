from featureflow import BaseModel, JSONFeature, ByteStream, ByteStreamFeature
from zounds.soundfile import \
    MetaData, AudioMetaDataEncoder, OggVorbis, OggVorbisFeature, AudioStream, \
    Resampler
from zounds.timeseries import ConstantRateTimeSeriesFeature, SR44100, HalfLapped
from zounds.spectral import \
    SlidingWindow, OggVorbisWindowingFunc, FFT, BarkBands


def audio_graph(
        chunksize_bytes=2 * 44100 * 30 * 2,
        resample_to=SR44100(),
        freesound_api_key=None,
        store_fft=False):
    """
    Produce a base class suitable as a starting point for many audio processing
    pipelines.  This class resamples all audio to a common sampling rate, and
    produces a bark band spectrogram from overlapping short-time fourier
    transform frames.  It also compresses the audio into ogg vorbis format for
    compact storage.
    """

    class AudioGraph(BaseModel):
        meta = JSONFeature(
                MetaData,
                freesound_api_key=freesound_api_key,
                store=True,
                encoder=AudioMetaDataEncoder)

        raw = ByteStreamFeature(
                ByteStream,
                chunksize=chunksize_bytes,
                needs=meta,
                store=False)

        ogg = OggVorbisFeature(
                OggVorbis,
                needs=raw,
                store=True)

        pcm = ConstantRateTimeSeriesFeature(
                AudioStream,
                needs=raw,
                store=False)

        resampled = ConstantRateTimeSeriesFeature(
                Resampler,
                needs=pcm,
                samplerate=resample_to)

        windowed = ConstantRateTimeSeriesFeature(
                SlidingWindow,
                needs=resampled,
                wscheme=HalfLapped(),
                wfunc=OggVorbisWindowingFunc(),
                store=False)

        fft = ConstantRateTimeSeriesFeature(
                FFT,
                needs=windowed,
                store=store_fft)

        short_windowed = ConstantRateTimeSeriesFeature(
                SlidingWindow,
                needs=resampled,
                wscheme=HalfLapped(512, 256),
                wfunc=OggVorbisWindowingFunc(),
                store=False)

        short_fft = ConstantRateTimeSeriesFeature(
                FFT,
                needs=short_windowed,
                store=store_fft)

        bark = ConstantRateTimeSeriesFeature(
                BarkBands,
                needs=fft,
                samplerate=resample_to,
                store=True)

    return AudioGraph