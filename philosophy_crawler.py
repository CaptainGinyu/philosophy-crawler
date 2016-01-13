import urllib.request

'''
Gets the title of the Wikipedia page when passed in a string representation
of the HTML source of a Wikipedia page
under the assumption that the title of the page is contained within the first
occurrence of an h1 tag of a Wikipedia page, which seems to be the case for
pretty much every Wikipedia article
'''
def get_page_title(page):
    #Finds the location of the spot right before the ending h1 tag
    #Btw, I'm starting from the end because the beginning h1 tag also has a
    #bunch of attributes tacked on that I don't want to deal with...
    #specifically... <h1 id="firstHeading" class="firstHeading" lang="en">
    curr_index = page.find("</h1>") - 1

    #Gets the character at the index determined previously
    #This is the ending character of the title
    curr_char = page[curr_index]

    #We toss out all the stuff prior to the index determined before
    #so that the later functions (see other functions) will not have to look
    #through too much stuff
    #Then we store it in page_to_return, which will get returned along with
    #the title at the end
    page_to_return = page[curr_index:]

    #start with an empty string, then while we haven't reached the end of the
    #beginning h1 tag, which is marked by ">, the last characters in
    #<h1 id="firstHeading" class="firstHeading" lang="en">, we will keep
    #adding on characters until we have our title... backwards
    #which we then make forwards
    title = ""
    while not (curr_char == '>' and page[curr_index - 1] == '\"'):
        title += curr_char
        curr_index -= 1
        curr_char = page[curr_index]
    title = title[::-1]
    
    return (page_to_return, title)

'''
Gets the first valid a tag (link), which is an a tag which is not contained
within parenthesis and not italicized, given the string representation of
the HTML source of a Wikipedia page (which should have been trimmed down by now)
'''
def get_valid_a_tag(page):
    #find first occurrence of start of a tag in general
    curr_index = page.find("<a")
    
    while True:
        #Check to see if any open parenthesis or start of i tag from start
        #of page to where the start of a tag is
        paren = page.find("(", 0, curr_index) != -1
        ital_tag = page.find("<i", 0, curr_index) != -1

        #If no open parenthesis or start of i tag found up till the start of
        #the a tag, we're done
        if not paren and not ital_tag:
            break

        #Otherwise, check go past the ending parenthesis or ending i tag
        #and find the next start of an a tag
        if paren:
            curr_index = page.find(")")
            page = page[(curr_index + 1):]
        elif ital_tag:
            curr_index = page.find("/i>")
            page = page[(curr_index + 3):]
        curr_index = page.find("<a")

    #We return both the trimmed down page and the index of the found
    #valid a tag
    return (page, curr_index)

'''
Get the first valid link (not in parenthesis or italicized)
of a Wikipedia article, given a string representation of the HTML source of a
Wikipedia page (which should have been trimmed down by now)

Assumes certain things about the format of the source of an article, as
stated in comments below
'''
def get_first_link(page):
    #We assume that the main content of the article starts right after the first
    #occurence of a p tag... we want start of the main content because
    #we want to ignore the links that are not the main content (like the links
    #at the top of a Wikipedia page)
    #However, while this is the case for a lot of Wikipedia articles, this seems
    #to have a few exceptions... for example, the Wikipedia article for "Human"
    #But otherwise, this assumption seems to be good enough
    start_index = page.find("<p>") + 3
    page = page[start_index:]

    while True:
        wiki_link = ""
        page, curr_index = get_valid_a_tag(page)

        #Here, we assume that Wikipedia article links are linked using
        #href="/wiki/ right after the a tag
        #The exception to this (Wikipedia Help pages) is handled below
        curr_index = page.find("href=\"/wiki/") + 12

        #Appending characters to our link to return while we haven't hit the
        #ending quotation marks that belong to the href
        curr_char = page[curr_index]
        while curr_char != '\"':
            wiki_link += curr_char
            curr_index += 1
            curr_char = page[curr_index]

        #If the link that we got is not a Wikipedia help page, which
        #would have Help: in it if it did, we are done
        if wiki_link.find("Help:") == -1:
            break

        #otherwise, we trim down the page, and get next link through next
        #iteration of this loop
        page = page[curr_index:]
    
    return wiki_link


'''
Takes a step toward the Philosophy article given a string representing the
title of the Wikipedia article to navigate to
'''
def step_toward_philosophy(topic):
    try:
        #navigating to the Wikipedia page
        with urllib.request.urlopen("http://en.wikipedia.org/wiki/" + topic) as response:
            page = str(response.read())   

        #stop if we get to a non-existent article
        if page.find("does not have an article with this exact name") != -1:
            print("Got to a non-existent article... Try another starting topic")
            return ("", "")

        #stop if we get to a non-article Wikipedia page (ie. Help page)
        if page.find("Article</a></span></li>") == -1:
            print("Got to non-article Wikipedia page... Try another starting topic")
            return ("", "")
            
        page, title = get_page_title(page)    
        print(title)
        if title == "Philosophy":
            return (title, "")
        next_topic = get_first_link(page)

        return (title, next_topic)

    except:
        #Case for if we get an error or get to non-existent article
        print("Got to a non-existent article (or error)... Try another starting topic")
        return ("", "")

'''
Gets user input and replaces spaces with underscores
(because Wikipedia URLs replace spaces with underscores)
'''
def get_starting_topic():
    starting_topic = input("Enter starting Wikipedia topic: ")
    for i in range(0, len(starting_topic)):
        if starting_topic[i] == ' ':
            starting_topic = starting_topic[:i] + '_' + starting_topic[(i + 1):]
    return starting_topic

def philosophy_crawl():
    num_steps = 0
    topic = get_starting_topic()
    title, topic = step_toward_philosophy(topic)
    while title == "":
        topic = get_starting_topic()
        title, topic = step_toward_philosophy(topic)
    num_steps += 1

    while title != "Philosophy":
        title, topic = step_toward_philosophy(topic)
        num_steps += 1
        if title == "":
            num_steps = 0
            topic = get_starting_topic()

    print("Got to philosophy in " + str(num_steps) + " steps!!!")

#main
if __name__ == "__main__":
    philosophy_crawl()
