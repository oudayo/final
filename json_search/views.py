from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.dateparse import parse_duration
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse
from urllib.parse import quote_plus
from rest_framework import status
from .models import *
import requests
# import pyaudio
from time import ctime
import webbrowser
import time
# import playsound
import os
import random


# from gtts import gTTS


class SearchView(APIView):
    permission_classes = (IsAdminUser,)
    renderer_classes = [JSONRenderer]

    def post(self, request):

        videos = []
        query = request.data.get("query")
        data_query = request.data.get("data_query", 1)
        video_query = request.data.get("video_query", 0)
        page_number = request.data.get('page', 0)
        level = int(request.data.get("reading_level", 1))
        api_key = "AIzaSyAt-w_yZPQwfYfhzgb6qyzSgzc1JBIcG-k"
        cx = "55643214e2b7c4c4e"

        if query == "" or query == None:
            return Response({"query requis"}, status=status.HTTP_400_BAD_REQUEST)

        quote_plus(query)
        items = []
        page_number = int(page_number) * 10 + 1

        try:
            response = requests.get(
                f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cx}&start={page_number}&num=10&gl=us")
            data = response.json()
            items = data["items"]
            search_url = 'https://www.googleapis.com/youtube/v3/search'
            video_url = 'https://www.googleapis.com/youtube/v3/videos'

            search_params = {
                'part': 'snippet',
                'q': query,
                'key': api_key,
                'maxResults': 10,
                'type': 'video'
            }

            r = requests.get(search_url, params=search_params)

            results = r.json()['items']
            video_ids = []
            for result in results:
                video_ids.append(result['id']['videoId'])

            video_params = {
                'key': api_key,
                'part': 'snippet,contentDetails',
                'id': ','.join(video_ids),
                'maxResults': 10
            }

            r = requests.get(video_url, params=video_params)

            results = r.json()['items']

            for result in results:
                video_data = {
                    'title': result['snippet']['title'],
                    'id': result['id'],
                    'url': f'https://www.youtube.com/watch?v={result["id"]}',
                    'duration': int(parse_duration(result['contentDetails']['duration']).total_seconds() // 60),
                    'thumbnail': result['snippet']['thumbnails']['high']['url']
                }

                videos.append(video_data)

        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if items:
            if level == 1:
                items = [
                    item for item in items if 'pagemap' in item and 'cse_image' in item['pagemap']]
            elif level == 2:
                items = [item for item in items if 'pagemap' in item and len(
                    item['snippet']) <= 200]
            elif level == 3:
                items = [item for item in items if len(item['snippet']) <= 150]
            elif level == 4:
                items = [item for item in items if 'pagemap' in item and len(
                    item['snippet']) >= 100]
            elif level == 5:
                items = [item for item in items]

            random.shuffle(items)
            random.shuffle(videos)

            if data_query == 1 and video_query == 0:
                return Response(items, status=status.HTTP_200_OK)
            if video_query == 1 and data_query == 0:
                return Response(videos, status=status.HTTP_200_OK)
            if data_query == 1 and video_query == 1:
                return Response({'items ': items, 'videos ': videos}, status=status.HTTP_200_OK)
        else:
            return Response({'na data'}, status=status.HTTP_204_NO_CONTENT)

