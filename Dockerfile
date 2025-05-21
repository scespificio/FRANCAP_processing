FROM ubuntu:latest
RUN apt-get update && apt-get install python3-pip -y && apt-get install python3-venv -y 
RUN python3 -m venv app-env
RUN apt-get install -y locales && locale-gen fr_FR.UTF-8 && update-locale LANG=fr_FR.UTF-8 && apt-get clean
ENV LANG=fr_FR.UTF-8
ENV LC_ALL=fr_FR.UTF-8
ENV LANGUAGE=fr_FR.UTF-8
ADD requirement.txt /app/requirement.txt
ADD /src/ /app/
RUN /bin/sh -c ". ../app-env/bin/activate && pip install -r /app/requirement.txt && python3 -m spacy download fr_core_news_md"
WORKDIR /app 
CMD /bin/sh -c ". ../app-env/bin/activate && streamlit run app.py --server.port 5890 > ./save/$(date +'%Y-%m-%d')_trace.log"
VOLUME ["/app/auth", "/app/config", "/app/save", "/app/static/PR2418", "/app/static/PR2419", "/app/static/PR2420", "/app/static/PR2421","/app/static/PR2422", "/app/static/PR2423"]
EXPOSE 5890

