

## ffmpeg

### Installation

[Static ffmpeg build](https://johnvansickle.com/ffmpeg/)


### Usage

```shell
ffmpeg  -framerate 25 -i img-%05d.png -vcodec libx264 -pix_fmt yuv420p -crf 30 ani.mp4
```