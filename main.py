from flask import Flask, request, jsonify, send_file
from pytube import YouTube
import re

app = Flask(__name__)

def get_short_link(link):
    return re.sub(r'shorts/', 'watch?v=', link)

@app.route('/get', methods=['POST'])
def get_link():
    # get the post data
    data = request.json
    # extract the link into a variable
    link = data['link']
    link = get_short_link(link) if 'shorts' in link else link
    # generate an object that contains the download link
    try:
        yt = YouTube(link)
    except:
        return jsonify({'error': 'Could be a network problem by the server or invalid video link, if the problem persists it is you problem.'})
    # todo: get the video title
    title = yt.title
    # todo: set the quality of the desired video
    disp_res = []
    for stream in yt.streams.filter(adaptive=True):
        disp_res.append(stream.resolution)
    disp_res = list(set([res for res in disp_res if res]))
    # todo: captions avalailability
    # captions = yt.captions.get_by_language_code('en')
    # print(captions.xml_captions) todo:
        # srt_format = (captions.generate_srt_captions())
        # print(srt_format)
    # todo: whether to get only the audio or video + audio
        # file size with audio only and diff video resolution
    audio_only = yt.streams.get_audio_only()
    # audio_quality = {}
    # for audio in audio_only:
    #     audio_quality['quality'] = audio.abr
    #     audio_quality['type'] = audio.mime_type

    return jsonify({'title': title, 'resolutions': disp_res, 'default_res': '360p'})
    

@app.route('/download', methods=['POST'])
def download():
    data = request.data
    link = data['link']
    yt = YouTube(link)
    if not data['audio']:
        if data['resolution']:
            if yt.streams.filter(res=data['resolution'],file_extension='mp4').filesize_mb > 250:
                return jsonify({'error': 'Sorry large file'})
            title = yt.title
            yt.streams.filter(res=data['resolution'],file_extension='mp4').first().download('Downloads/video/', filename=yt.title)

            video_path = f'Downloads/video/{title} + ".mp4"'
            return send_file(video_path, as_attachment=True)
        else:
            try:
                yt.streams.filter(res=data['def_res']).first().download('Downloads/video/', filename=yt.title)
                video_path = f'Downloads/video/{yt.title} + ".mp4"'
                return send_file(video_path, as_attachment=True)
            except:
                return jsonify({'error': 'Sorry a problem has occured'})
    else: 
        try:
            yt.streams.filter(only_audio=True)[0].download('Downloads/audio/', filename=yt.title)
            video_path = f'Downloads/video/{yt.title} + ".mp4"'
            return send_file(video_path, as_attachment=True)
        except:
            return jsonify({'error': 'Sorry a problem has occured'})

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'HAHA NICE TRY HEKER'}), 405

if __name__ == '__main__':
    app.run()