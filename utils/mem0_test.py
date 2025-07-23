import os
from mem0 import Memory

config = {
    "vector_store": {
        "provider": "milvus",
        "config": {
            "collection_name": "test1",
            "embedding_model_dims": "4096",
            "url": "http://10.1.180.8:19530",
            "token": "8e4b8ca8cf2c67",
        }
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "dengcao/Qwen3-Embedding-8B:Q4_K_M",
            "ollama_base_url": "http://10.1.180.8:11434"
        }
    },
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "qwen3:8b",
            "temperature": 0.1,
            "max_tokens": 10240,
            "ollama_base_url": "http://10.1.180.8:11434"
        }
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": "neo4j://10.1.180.8:7687",
            "username": "neo4j",
            "password": "damon123"
        }
    }
}

m = Memory.from_config(config)
messages = [
    {"role": "user", "content": "I'm planning to watch a movie tonight. Any recommendations?"},
    {"role": "assistant", "content": "How about a thriller movies? They can be quite engaging."},
    {"role": "user", "content": "I’m not a big fan of thriller movies but I love sci-fi movies."},
    {"role": "assistant", "content": "Got it! I'll avoid thriller recommendations and suggest sci-fi movies in the future."}
]

data = [
    {"messages": "Learning how to build a drone from scratch.", "user_id": "frank", "metadata": {"category": "technology"}},
    {"messages": "Exploring DIY furniture making.", "user_id": "grace", "metadata": {"category": "crafts"}},
    {"messages": "Practicing French vocabulary every morning.", "user_id": "helen", "metadata": {"category": "language"}},
    {"messages": "Working on a side project in machine learning.", "user_id": "ian", "metadata": {"category": "technology"}},
    {"messages": "Getting into origami and paper folding art.", "user_id": "julia", "metadata": {"category": "art"}},
    {"messages": "Training for a local triathlon event.", "user_id": "kevin", "metadata": {"category": "fitness"}},
    {"messages": "I recently planted a small vegetable garden.", "user_id": "laura", "metadata": {"category": "lifestyle"}},
    {"messages": "Writing poetry during quiet afternoons.", "user_id": "michael", "metadata": {"category": "writing"}},
    {"messages": "Exploring the fundamentals of blockchain.", "user_id": "nina", "metadata": {"category": "finance"}},
    {"messages": "Building my own mechanical keyboard.", "user_id": "oliver", "metadata": {"category": "technology"}},
    {"messages": "Learning to play chess more strategically.", "user_id": "paula", "metadata": {"category": "games"}},
    {"messages": "Trying to recreate dishes from cooking shows.", "user_id": "quinn", "metadata": {"category": "food"}},
    {"messages": "I've started a bullet journal for productivity.", "user_id": "ron", "metadata": {"category": "productivity"}},
    {"messages": "Watching travel vlogs about Europe.", "user_id": "sara", "metadata": {"category": "travel"}},
    {"messages": "Taking an art history course online.", "user_id": "tom", "metadata": {"category": "education"}},
    {"messages": "Learning the ukulele through YouTube.", "user_id": "ursula", "metadata": {"category": "music"}},
    {"messages": "Following space exploration news daily.", "user_id": "victor", "metadata": {"category": "science"}},
    {"messages": "Writing short stories in my free time.", "user_id": "wendy", "metadata": {"category": "writing"}},
    {"messages": "Experimenting with minimalism at home.", "user_id": "xander", "metadata": {"category": "lifestyle"}},
    {"messages": "Starting to sketch with charcoal.", "user_id": "yasmin", "metadata": {"category": "art"}},
    {"messages": "Designing my own mobile app.", "user_id": "zack", "metadata": {"category": "technology"}},
    {"messages": "Practicing mindfulness with guided apps.", "user_id": "alice", "metadata": {"category": "wellness"}},
    {"messages": "Brewing kombucha at home.", "user_id": "bob", "metadata": {"category": "food"}},
    {"messages": "Learning historical facts through podcasts.", "user_id": "carol", "metadata": {"category": "history"}},
    {"messages": "Reading up on climate change reports.", "user_id": "dave", "metadata": {"category": "science"}},
    {"messages": "Starting a YouTube channel on game reviews.", "user_id": "eva", "metadata": {"category": "entertainment"}},
    {"messages": "Knitting a winter scarf by hand.", "user_id": "frank", "metadata": {"category": "crafts"}},
    {"messages": "Hiking a new trail every weekend.", "user_id": "grace", "metadata": {"category": "travel"}},
    {"messages": "Building a Raspberry Pi weather station.", "user_id": "helen", "metadata": {"category": "technology"}},
    {"messages": "Exploring surrealist painting techniques.", "user_id": "ian", "metadata": {"category": "art"}},
    {"messages": "Collecting retro video game consoles.", "user_id": "julia", "metadata": {"category": "collection"}},
    {"messages": "Trying intermittent fasting for health.", "user_id": "kevin", "metadata": {"category": "wellness"}},
    {"messages": "Reading philosophical essays.", "user_id": "laura", "metadata": {"category": "education"}},
    {"messages": "Volunteering to teach coding basics to kids.", "user_id": "michael", "metadata": {"category": "community"}},
    {"messages": "Baking pastries every weekend.", "user_id": "nina", "metadata": {"category": "food"}},
    {"messages": "Working through a puzzle book series.", "user_id": "oliver", "metadata": {"category": "games"}},
    {"messages": "Streaming acoustic covers live.", "user_id": "paula", "metadata": {"category": "music"}},
    {"messages": "Tracking expenses using budgeting apps.", "user_id": "quinn", "metadata": {"category": "finance"}},
    {"messages": "Rewatching classic 80s comedies.", "user_id": "ron", "metadata": {"category": "movies"}},
    {"messages": "Trying to understand neural networks.", "user_id": "sara", "metadata": {"category": "technology"}},
    {"messages": "Writing daily reflections in a gratitude journal.", "user_id": "tom", "metadata": {"category": "wellness"}},
    {"messages": "Making educational reels on Instagram.", "user_id": "ursula", "metadata": {"category": "content"}},
    {"messages": "Decorating my room with handmade crafts.", "user_id": "victor", "metadata": {"category": "crafts"}},
    {"messages": "Following Formula 1 racing closely.", "user_id": "wendy", "metadata": {"category": "sports"}},
    {"messages": "Practicing yoga on the beach at sunrise.", "user_id": "xander", "metadata": {"category": "fitness"}},
    {"messages": "Learning SQL for data analysis.", "user_id": "yasmin", "metadata": {"category": "skills"}},
    {"messages": "Writing fan fiction based on fantasy series.", "user_id": "zack", "metadata": {"category": "writing"}},
    {"messages": "Trying to memorize the periodic table.", "user_id": "alice", "metadata": {"category": "education"}},
    {"messages": "Curating playlists by mood and genre.", "user_id": "bob", "metadata": {"category": "music"}},
    {"messages": "Collecting postage stamps from different eras.", "user_id": "carol", "metadata": {"category": "collection"}},
    {"messages": "DIY home automation projects using Arduino.", "user_id": "dave", "metadata": {"category": "technology"}},
    {"messages": "Watching indie films from international festivals.", "user_id": "eva", "metadata": {"category": "movies"}},
    {"messages": "Joining a local pottery class.", "user_id": "frank", "metadata": {"category": "art"}},
    {"messages": "Training for a half marathon.", "user_id": "grace", "metadata": {"category": "fitness"}},
    {"messages": "Writing code for a personal finance tracker.", "user_id": "helen", "metadata": {"category": "finance"}},
    {"messages": "Learning how to DJ with electronic music.", "user_id": "ian", "metadata": {"category": "music"}},
    {"messages": "Attending virtual seminars on psychology.", "user_id": "julia", "metadata": {"category": "education"}},
    {"messages": "Creating animated shorts for fun.", "user_id": "kevin", "metadata": {"category": "animation"}},
    {"messages": "Documenting my plant growth journey.", "user_id": "laura", "metadata": {"category": "lifestyle"}},
    {"messages": "Editing drone footage from last vacation.", "user_id": "michael", "metadata": {"category": "media"}},
    {"messages": "Trying new cocktail recipes each weekend.", "user_id": "nina", "metadata": {"category": "food"}},
    {"messages": "Reviewing gadgets on my tech blog.", "user_id": "oliver", "metadata": {"category": "content"}},
    {"messages": "Sketching fashion designs for fun.", "user_id": "paula", "metadata": {"category": "fashion"}},
    {"messages": "Learning Korean to watch dramas without subtitles.", "user_id": "quinn", "metadata": {"category": "language"}},
    {"messages": "Running a newsletter about cybersecurity news.", "user_id": "ron", "metadata": {"category": "technology"}},
    {"messages": "Working on a game prototype using Unity.", "user_id": "sara", "metadata": {"category": "games"}},
    {"messages": "Exploring different meditation techniques.", "user_id": "tom", "metadata": {"category": "wellness"}},
]

for item in data:
    m.add(messages=item["messages"], user_id=item["user_id"], metadata=item["metadata"])


# res = m.add(
#     messages="I am working on improving my tennis skills.",
#     user_id="alice",
#     metadata={"category": "hobbies"},
# )
# print(res)
#m.add(messages, user_id="alice", metadata={"category": "movies"})
all_memories = m.get_all(user_id="alice")
print(all_memories)
