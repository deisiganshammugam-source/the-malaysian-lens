# How to Publish Your Website

## What is "hosting"?
Think of your website as a folder of files on your computer.
Hosting = putting that folder somewhere on the internet so others can visit it.
The free option below takes about 5 minutes.

---

## OPTION 1: Netlify Drop (Recommended — Free, No Account Needed)
This is the easiest. You literally drag and drop your folder.

1. Go to **https://app.netlify.com/drop**
2. Drag and drop your entire `my_website` folder onto the page
3. Netlify gives you a free URL like `https://amazing-name-123.netlify.app`
4. Done. Your site is live.

**Every time you update:** just drag and drop the folder again.

---

## OPTION 2: GitHub Pages (Free, with a cleaner URL)
Good if you want a URL like `deisigan.github.io`

1. Create a free account at **https://github.com**
2. Create a new repository called `my-website`
3. Upload all the files in this folder
4. Go to Settings → Pages → select "main branch" → Save
5. Your site goes live at `https://yourusername.github.io/my-website`

---

## How Claude Publishes a New Post
When you finish an analysis and want to post it:

1. Tell Claude: *"Write a post about [topic] for my website"*
2. Claude will fill in `new_post.py` with the article content
3. Claude runs `python3 new_post.py` — this creates the article HTML and updates the homepage
4. You re-upload the folder to Netlify (drag and drop again)

That's it.

---

## Your Website Files
```
my_website/
├── index.html              ← Homepage
├── articles/
│   └── semiconductors.html ← Sample article (your gold standard)
├── new_post.py             ← Claude uses this to publish posts
└── HOW_TO_PUBLISH.md       ← This file
```
