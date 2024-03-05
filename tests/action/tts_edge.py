import edge_tts
import asyncio

TEXT = "故事开始时，洛野第一次来到派出所，被误以为是私闯民宅的小偷。在派出所里，他被审问，但他的解释却引起了警察的怀疑。最终，洛野解释清楚了自己的情况，原来他是江城大学的新生，因为一系列误会，被误抓到派出所。洛野原本是为了追求高中暗恋三年的女神而来到江城大学，但却发现女神已经不再理睬他。"

print(TEXT)
voice = 'zh-CN-YunxiNeural'
output = './text2voicetest.mp3'
rate = '+4%'  # 语速
volume = '+0%'  # 音量


async def my_function():
    tts = edge_tts.Communicate(text=TEXT, voice=voice, rate=rate, volume=volume)
    await tts.save(output)


if __name__ == '__main__':
    asyncio.run(my_function())
