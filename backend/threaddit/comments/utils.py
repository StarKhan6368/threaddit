def create_comment_tree(comments, cur_user=None):
    if not comments[0]:
        return []
    comment_dict = {}
    root_comments = []

    for comment in comments:
        comment_data = {"comment": comment.as_dict(cur_user), "children": []}
        comment_dict[comment.comment_id] = comment_data

        if not comment.has_parent:
            root_comments.append(comment_data)
        elif comment.parent_id in comment_dict:
            comment_dict[comment.parent_id]["children"].append(comment_data)
    return root_comments
