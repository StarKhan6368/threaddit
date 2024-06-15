CREATE TABLE public.comments (
    id integer NOT NULL,
    user_id integer NOT NULL,
    post_id integer NOT NULL,
    parent_id integer,
    has_parent boolean,
    content text NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    is_edited boolean DEFAULT false
);


CREATE TABLE public.posts (
    id integer NOT NULL,
    user_id integer NOT NULL,
    subthread_id integer NOT NULL,
    title text NOT NULL,
    media text,
    content text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    is_edited boolean DEFAULT false
);


CREATE TABLE public.reactions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    post_id integer,
    comment_id integer,
    is_upvote boolean NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE public.users (
    id integer NOT NULL,
    username text NOT NULL,
    password_hash text NOT NULL,
    email text NOT NULL,
    avatar text,
    bio text,
    registration_date timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


CREATE VIEW public.comment_info AS
 SELECT c.id AS comment_id,
    u.username AS user_name,
    u.avatar AS user_avatar,
    ckarma.comment_karma,
    c.has_parent,
    c.parent_id,
    c.is_edited,
    c.content,
    c.created_at,
    p.id AS post_id
   FROM (((public.posts p
     FULL JOIN public.comments c ON ((c.post_id = p.id)))
     FULL JOIN ( SELECT c_1.id AS comment_id,
            COALESCE(sum(
                CASE
                    WHEN (r.is_upvote = true) THEN 1
                    WHEN (r.is_upvote = false) THEN '-1'::integer
                    ELSE 0
                END), (0)::bigint) AS comment_karma
           FROM (public.comments c_1
             FULL JOIN public.reactions r ON ((r.comment_id = c_1.id)))
          GROUP BY c_1.id
         HAVING (c_1.id IS NOT NULL)) ckarma ON ((ckarma.comment_id = c.id)))
     FULL JOIN public.users u ON ((u.id = c.user_id)));

CREATE SEQUENCE public.comments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.comments_id_seq OWNED BY public.comments.id;

CREATE TABLE public.messages (
    id integer NOT NULL,
    sender_id integer NOT NULL,
    receiver_id integer NOT NULL,
    content text NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    seen boolean DEFAULT false NOT NULL,
    seen_at timestamp with time zone
);

CREATE SEQUENCE public.messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.messages_id_seq OWNED BY public.messages.id;

CREATE TABLE public.subthreads (
    id integer NOT NULL,
    name character varying(20) NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    logo text,
    created_by integer
);

CREATE VIEW public.post_info AS
 SELECT t.id AS thread_id,
    t.name AS thread_name,
    t.logo AS thread_logo,
    p.id AS post_id,
    k.karma AS post_karma,
    p.title,
    p.media,
    p.is_edited,
    p.content,
    p.created_at,
    u.id AS user_id,
    u.username AS user_name,
    u.avatar AS user_avatar,
    c.comments_count
   FROM ((((public.posts p
     JOIN ( SELECT p_1.id AS post_id,
            COALESCE(sum(
                CASE
                    WHEN (r.is_upvote = true) THEN 1
                    WHEN (r.is_upvote = false) THEN '-1'::integer
                    ELSE 0
                END), (0)::bigint) AS karma
           FROM (public.posts p_1
             FULL JOIN public.reactions r ON ((r.post_id = p_1.id)))
          GROUP BY p_1.id) k ON ((k.post_id = p.id)))
     JOIN ( SELECT p_1.id AS post_id,
            count(c_1.id) AS comments_count
           FROM (public.posts p_1
             FULL JOIN public.comments c_1 ON ((c_1.post_id = p_1.id)))
          GROUP BY p_1.id) c ON ((c.post_id = p.id)))
     JOIN public.subthreads t ON ((t.id = p.subthread_id)))
     JOIN public.users u ON ((u.id = p.user_id)));

CREATE SEQUENCE public.posts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.posts_id_seq OWNED BY public.posts.id;

CREATE SEQUENCE public.reactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.reactions_id_seq OWNED BY public.reactions.id;

CREATE TABLE public.roles (
    id integer NOT NULL,
    name text NOT NULL,
    slug text NOT NULL
);

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;

CREATE TABLE public.saved (
    id integer NOT NULL,
    user_id integer NOT NULL,
    post_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE SEQUENCE public.saved_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.saved_id_seq OWNED BY public.saved.id;

CREATE TABLE public.subscriptions (
    id integer NOT NULL,
    user_id integer  NOT NULL,
    subthread_id integer  NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE SEQUENCE public.subscriptions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.subscriptions_id_seq OWNED BY public.subscriptions.id;

CREATE VIEW public.subthread_info AS
 SELECT subthreads.id,
    subthreads.name,
    subthreads.logo,
    mcount.members_count,
    pcount.posts_count,
    ccount.comments_count
   FROM (((public.subthreads
     FULL JOIN ( SELECT subthreads_1.id AS subthread_id,
            count(*) AS members_count
           FROM (public.subthreads subthreads_1
             JOIN public.subscriptions ON ((subscriptions.subthread_id = subthreads_1.id)))
          GROUP BY subthreads_1.id) mcount ON ((mcount.subthread_id = subthreads.id)))
     FULL JOIN ( SELECT subthreads_1.id AS subthread_id,
            count(*) AS posts_count
           FROM (public.subthreads subthreads_1
             JOIN public.posts ON ((posts.subthread_id = subthreads_1.id)))
          GROUP BY subthreads_1.id) pcount ON ((pcount.subthread_id = subthreads.id)))
     FULL JOIN ( SELECT subthreads_1.id AS subthread_id,
            count(*) AS comments_count
           FROM ((public.subthreads subthreads_1
             JOIN public.posts ON ((posts.subthread_id = subthreads_1.id)))
             JOIN public.comments ON ((comments.post_id = posts.id)))
          GROUP BY subthreads_1.id) ccount ON ((ccount.subthread_id = subthreads.id)));

CREATE SEQUENCE public.subthreads_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.subthreads_id_seq OWNED BY public.subthreads.id;

CREATE VIEW public.user_info AS
 SELECT u.id AS user_id,
    (c.karma + p.karma) AS user_karma,
    c.comments_count,
    c.karma AS comments_karma,
    p.posts_count,
    p.karma AS posts_karma
   FROM ((public.users u
     JOIN ( SELECT u_1.id AS user_id,
            count(c_1.id) AS comments_count,
            COALESCE(sum(
                CASE
                    WHEN ((r.is_upvote = true) AND (r.comment_id IS NOT NULL)) THEN 1
                    WHEN ((r.is_upvote = false) AND (r.comment_id IS NOT NULL)) THEN '-1'::integer
                    ELSE 0
                END), (0)::bigint) AS karma
           FROM ((public.users u_1
             FULL JOIN public.comments c_1 ON ((c_1.user_id = u_1.id)))
             FULL JOIN public.reactions r ON ((r.comment_id = c_1.id)))
          GROUP BY u_1.id) c ON ((c.user_id = u.id)))
     JOIN ( SELECT u_1.id AS user_id,
            count(p_1.id) AS posts_count,
            COALESCE(sum(
                CASE
                    WHEN ((r.is_upvote = true) AND (r.post_id IS NOT NULL)) THEN 1
                    WHEN ((r.is_upvote = false) AND (r.post_id IS NOT NULL)) THEN '-1'::integer
                    ELSE 0
                END), (0)::bigint) AS karma
           FROM ((public.users u_1
             FULL JOIN public.posts p_1 ON ((p_1.user_id = u_1.id)))
             FULL JOIN public.reactions r ON ((r.post_id = p_1.id)))
          GROUP BY u_1.id) p ON ((p.user_id = u.id)));

CREATE TABLE public.user_roles (
    id integer NOT NULL,
    user_id integer NOT NULL,
    role_id integer NOT NULL,
    subthread_id integer,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE SEQUENCE public.user_roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.user_roles_id_seq OWNED BY public.user_roles.id;

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;

ALTER TABLE ONLY public.comments ALTER COLUMN id SET DEFAULT nextval('public.comments_id_seq'::regclass);

ALTER TABLE ONLY public.messages ALTER COLUMN id SET DEFAULT nextval('public.messages_id_seq'::regclass);

ALTER TABLE ONLY public.posts ALTER COLUMN id SET DEFAULT nextval('public.posts_id_seq'::regclass);

ALTER TABLE ONLY public.reactions ALTER COLUMN id SET DEFAULT nextval('public.reactions_id_seq'::regclass);

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);

ALTER TABLE ONLY public.saved ALTER COLUMN id SET DEFAULT nextval('public.saved_id_seq'::regclass);

ALTER TABLE ONLY public.subscriptions ALTER COLUMN id SET DEFAULT nextval('public.subscriptions_id_seq'::regclass);

ALTER TABLE ONLY public.subthreads ALTER COLUMN id SET DEFAULT nextval('public.subthreads_id_seq'::regclass);

ALTER TABLE ONLY public.user_roles ALTER COLUMN id SET DEFAULT nextval('public.user_roles_id_seq'::regclass);

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.reactions
    ADD CONSTRAINT reactions_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.reactions
    ADD CONSTRAINT reactions_user_id_comment_id_key UNIQUE (user_id, comment_id);

ALTER TABLE ONLY public.reactions
    ADD CONSTRAINT reactions_user_id_post_id_key UNIQUE (user_id, post_id);

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_name_key UNIQUE (name);

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_slug_key UNIQUE (slug);

ALTER TABLE ONLY public.saved
    ADD CONSTRAINT saved_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.saved
    ADD CONSTRAINT saved_user_id_post_id_key UNIQUE (user_id, post_id);

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_pkey PRIMARY KEY (id);
    
ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_user_id_subthread_id_key UNIQUE (user_id, subthread_id);

ALTER TABLE ONLY public.subthreads
    ADD CONSTRAINT subthreads_name_key UNIQUE (name);

ALTER TABLE ONLY public.subthreads
    ADD CONSTRAINT subthreads_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_user_id_role_id_subthread_id_key UNIQUE (user_id, role_id, subthread_id);

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.comments(id) ON UPDATE CASCADE ON DELETE CASCADE NOT VALID;

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.posts(id) ON UPDATE CASCADE ON DELETE CASCADE NOT VALID;

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE NOT VALID;

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_receiver_id_fkey FOREIGN KEY (receiver_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE NOT VALID;

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_sender_id_fkey FOREIGN KEY (sender_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE NOT VALID;

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_subthread_id_fkey FOREIGN KEY (subthread_id) REFERENCES public.subthreads(id) ON UPDATE CASCADE ON DELETE CASCADE NOT VALID;

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE NOT VALID;

ALTER TABLE ONLY public.reactions
    ADD CONSTRAINT reactions_comment_id_fkey FOREIGN KEY (comment_id) REFERENCES public.comments(id) ON UPDATE CASCADE ON DELETE CASCADE NOT VALID;

ALTER TABLE ONLY public.reactions
    ADD CONSTRAINT reactions_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.posts(id) ON UPDATE CASCADE ON DELETE CASCADE NOT VALID;

ALTER TABLE ONLY public.reactions
    ADD CONSTRAINT reactions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE NOT VALID;

ALTER TABLE ONLY public.saved
    ADD CONSTRAINT saved_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.posts(id) ON UPDATE CASCADE ON DELETE CASCADE NOT VALID;

ALTER TABLE ONLY public.saved
    ADD CONSTRAINT saved_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE NOT VALID;

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_subthread_id_fkey FOREIGN KEY (subthread_id) REFERENCES public.subthreads(id) ON UPDATE CASCADE ON DELETE CASCADE NOT VALID;

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE NOT VALID;
    
ALTER TABLE ONLY public.subthreads
    ADD CONSTRAINT subthreads_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE SET NULL NOT VALID;

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON UPDATE CASCADE ON DELETE CASCADE NOT VALID;

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_subthread_id_fkey FOREIGN KEY (subthread_id) REFERENCES public.subthreads(id) ON UPDATE CASCADE ON DELETE CASCADE NOT VALID;

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE NOT VALID;

INSERT INTO roles(name, slug) VALUES 
	('Thread Moderator','mod'),
	('Administrator', 'admin');