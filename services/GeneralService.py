from sqlalchemy.orm import Query

def applySearch(query: Query, model, fields: list[str], keyword: str):
    if keyword and fields:
        filters = []
        for fieldName in fields:
            field = getattr(model, fieldName, None)
            if field is not None:
                filters.append(field.ilike(f"%{keyword}%"))
        if filters:
            query = query.filter(*filters)
    return query