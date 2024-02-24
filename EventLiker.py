import json
import Like, Filepaths

def likes_reader():
    like_list = []

    try:

        with open(Filepaths.likes_file, "r") as file:
            content = file.read()

        modified_content = content.replace("}]", "},\n]")
        data = json.loads(modified_content)

        for event_data in data:
            like = Like.Like(event_data['id'])
            like.likers = event_data['likers']
            like_list.append(like)


    except FileNotFoundError:
        print("File not found!")
        try:
            with open(Filepaths.likes_file, "w") as f:
                print("File created!")

        except:
            print("Something went wrong!")


    except json.JSONDecodeError:
        print("Invalid JSON data in the file!")

    #except Exception:
     #   print("Something went wrong with the event reading from jsons")

    return like_list

def likes_writer(like_list):
    try:
        with open(Filepaths.likes_file, "w") as f:
            json.dump(like_list, f, cls=Like.LikeEncoder, indent=4, separators=(',', ': '))
            print(f"Likes saved to {Filepaths.likes_file}")


    except FileNotFoundError:
        print("Something went wrong")

def event_liker(user_id, event_id):
    print(user_id)
    #event in this file is NOT an Event.py type, it is Like.py type

    event_like_list = likes_reader()
    event_found = False
    for event in event_like_list:

        if event_id == event.id:

            event_found = True
            like_found = False

            for liker in event.likers:
                try:
                    liker = int(liker)
                except Exception:
                    print("Values don't mach :(")
                if liker == user_id:
                    like_found = True
            if like_found:
                return
            event.likers.append(user_id)


    if event_found == False:
        event = Like.Like(event_id)
        event.likers.append(user_id)
        print(event)
        event_like_list.append(event)

    print(f"event likes: {event_like_list}")

    likes_writer(event_like_list)



def like_counter(event_id):
    event_list = likes_reader()
    count = 0
    for event in event_list:
        if event_id == event.id:
            for like in event.likers:
                count += 1
    return count