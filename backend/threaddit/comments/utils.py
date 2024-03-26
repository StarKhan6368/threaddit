from typing_extensions import TYPE_CHECKING

if TYPE_CHECKING:
    from threaddit.comments.models import Comments


def create_comment_tree(comments: list["Comments"], cur_user: int | None = None):
    if not comments:
        return []

    comment_dict = {}
    root_comments = []

    for comment in comments:
        comment_data = {"comment": comment.as_dict(cur_user), "children": []}
        comment_dict[comment.id] = comment_data

        if not comment.has_parent:
            root_comments.append(comment_data)
        elif comment.parent_id in comment_dict:
            comment_dict[comment.parent_id]["children"].append(comment_data)

    return root_comments
