from fastapi import APIRouter, Depends

from Fast.dependencies import get_rag_service
from Fast.schemas import QueryRequest, QueryResponse, RetrieveRequest, RetrieveResponse

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def query(payload: QueryRequest, rag_service=Depends(get_rag_service)):
    result = rag_service.query_and_summarize(
        query=payload.query,
        top_k=payload.top_k,
        include_sources=payload.include_sources,
    )
    return QueryResponse(**result)


@router.post("/retrieve", response_model=RetrieveResponse)
def retrieve(payload: RetrieveRequest, rag_service=Depends(get_rag_service)):
    results = rag_service.retrieve(query=payload.query, top_k=payload.top_k)
    return RetrieveResponse(query=payload.query, results=results, count=len(results))
