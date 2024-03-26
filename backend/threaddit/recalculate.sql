-- The App should keep an accurate count, but just in case 
-- This script recalculates all the counts based on the current state of the database.
-- Using Views.

-- USERS

UPDATE users
set comment_karma = ui.comment_karma,
	post_count = ui.post_count,
	comment_count = ui.comment_count,
	post_karma = ui.post_karma
from user_info as ui
where users.id = ui.user_id;

-- SUBTHREADS

UPDATE subthreads
set subscriber_count = si.subscriber_count,
	post_count = si.post_count,
	comment_count = si.comment_count
from subthread_info as si
	where subthreads.id = si.subthread_id;
	
-- POSTS

UPDATE posts
set karma_count = pi.post_karma,
	comment_count = pi.comment_count
from post_info as pi
	where posts.id = pi.post_id;
	
-- COMMENTS

UPDATE comments
set karma_count = ci.comment_karma
from comment_info as ci
	where comments.id = ci.comment_id;
