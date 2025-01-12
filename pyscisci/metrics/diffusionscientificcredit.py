# -*- coding: utf-8 -*-
"""
.. module:: diffusionscientificcredit
    :synopsis: Rank authors based on the pagerank within their citation graph.

.. moduleauthor:: Alex Gates <ajgates42@gmail.com>
 """

import pandas as pd
import numpy as np

from pyscisci.utils import isin_sorted, groupby_count, groupby_total
from pyscisci.network import cocitation_network
from pyscisci.sparsenetworkutils import dataframe2bipartite, sparse_pagerank_scipy

def diffusion_of_scientific_credit(pub2ref_df, pub2author_df, pub_df=None, alpha = 0.9, max_iter = 100, tol = 1.0e-10):
    """
    Calculate the diffusion of scientific credits for each author based on :cite:`Radicchi2009authorpagerank`.

    Parameters
    ----------

    :param pub2ref_df : DataFrame
        A DataFrame with the citation information for each Publication.

    :param pub2author_df : DataFrame
        A DataFrame with the author information for each Publication.

    :param pub_df : DataFrame
        A DataFrame with the publication information for each Publication.

    :param alpha : float, default 0.9
        The PageRank reset probility

    :param max_iter : int, default 100
        The maximum number of iterations when appllying the power method.

    :param tol : float, default 1.0e-10
        The error tolerance when appllying the power method.

    Returns
    -------
    credit_share, numpy array
        If temporal == False:
            The adjacency matrix for the co-citation network

        If temporal == True:
            A dictionary with key for each year, and value of the adjacency matrix for the cocitation network induced
            by citing publications in that year.

    author2int, dict
        A mapping of the AuthorIds from the focus publication to the column of the credit share vector or matrix (see above).

    """

    """
    Diffusion of Scientific Credits and the Ranking of Scientists
    Radicchi et al (2009) Phys Rev E


    author_subset_df - each row is one article & author combination.  
            at least two columns 'name':author name, and 'teamsize':number of total authors on the paper

    full_citation_df - each row is one citation from one article & author combination
            at least four columns 'name_citing': name of citing author, 'name_cited': name of cited author, 
            'teamsize_citing': number of authors for citing paper, 'teamsize_cited': number of authors for cited papers.
    """

    # relabel the authors to map to network nodes
    focus_authors = np.sort(pub2author_df['AuthorId'].unique())
    author2int = {aid:i for i, aid in enumerate(focus_authors)}
    Nauthors = len(author2int)

    pub2author_df.drop_duplicates(subset=['PublicationId', 'AuthorId'], inplace=True)
    pub2author_df['AuthorId'] = [author2int.get(aid, None) for aid in pub2author_df['AuthorId'].values]

    # check if we are given the teamsize in publication information
    if (not pub_df is None) and 'TeamSize' in list(pub_df):
        teamsize = {pid:ts for pid, ts in pub_df[['PublicationId', 'TeamSize']].values}
    
    # otherwies we need to calculate teamsize based on the authorship information
    else:
        teamsize = pub2author_df.groupby('PublicationId')['AuthorId'].nunique()


    full_citation_df = pub2ref_df.merge(pub2author_df[['PublicationId', 'AuthorId']], left_on = 'CitingPublicationId', right_on = 'PublicationId')
    del full_citation_df['PublicationId']
    full_citation_df.rename(columns={'AuthorId':'CitingAuthorId'}, inplace=True)

    full_citation_df = full_citation_df.merge(pub2author_df[['PublicationId', 'AuthorId']], left_on = 'CitedPublicationId', right_on = 'PublicationId')
    del full_citation_df['PublicationId']
    full_citation_df.rename(columns={'AuthorId':'CitedAuthorId'}, inplace=True)

    full_citation_df.dropna(inplace=True)

    # now add in the teamsize information to make edge weights
    full_citation_df['edge_weight'] = [1.0/(teamsize.get(citing_pid, 1) * teamsize.get(cited_pid, 1)) for citing_pid, cited_pid in full_citation_df[['CitingPublicationId', 'CitedPublicationId']].values]


    adj_mat = dataframe2bipartite(full_citation_df, rowname='CitingAuthorId', colname='CitedAuthorId', 
        shape = (Nauthors,Nauthors), weightname = 'edge_weight')


    # make the weighted productivity vector to intialize the pagerank
    pub2author_df['AuthorCredit'] = [1/teamsize.get(pid, 1) for pid in pub2author_df['PublicationId'].values]
    weighted_productivity = groupby_total(pub2author_df, colgroupby = 'AuthorId', colcountby = 'AuthorCredit').sort_values('AuthorId')
    # norm vector
    weighted_productivity['AuthorCreditTotal'] = weighted_productivity['AuthorCreditTotal'] / weighted_productivity['AuthorCreditTotal'].sum()

    # run the power method to solve the diffusion 
    sc = sparse_pagerank_scipy(adj_mat, alpha= alpha, 
        personalization=weighted_productivity['AuthorCreditTotal'].values, 
        initialization=weighted_productivity['AuthorCreditTotal'].values,
                   max_iter=max_iter, tol=tol, dangling=None)

    return sc, author2int
