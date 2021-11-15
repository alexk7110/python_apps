#!/usr/bin/env python
# coding: utf-8

from sqlalchemy import create_engine
import pyodbc
import pymysql
import pandas as pd
import urllib

params = urllib.parse.quote_plus("DRIVER={SQL Server};SERVER=ELAST\\SQLEXPRESS;DATABASE=Elast;UID=db_username;PWD=replace_with_working_pass")


# Softone connection and query
sqlEngine       = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
dbConnection    = sqlEngine.connect()
dfs1            = pd.read_sql(" SELECT A.MTRL, A.CODE, A.NAME, ISNULL(B.QTY1,0) AS QTY1, ISNULL((SELECT SUM(dbo.fnSOGetLinePend(Z1.FINDOC,Z1.MTRLINES)) AS RESERVED FROM MTRLINES Z1, RESTMODE Z2 WHERE Z1.MTRL = A.MTRL AND Z1.COMPANY=1001 AND Z1.PENDING=1 AND Z2.RESTCATEG=2 AND Z2.COMPANY = 1001 AND Z1.RESTMODE = Z2.RESTMODE AND Z1.WHOUSE IN (SELECT WHOUSE FROM WHOUSE WHERE CUSTOMSTYPE=0 AND COMPANY=1001)),0) AS RSRVD FROM MTRL A LEFT OUTER JOIN MTRDATA B ON B.COMPANY=1001 AND A.MTRL=B.MTRL AND B.FISCPRD=2021 WHERE A.COMPANY=1001 AND A.SODTYPE=51 ORDER BY A.CODE                                ;", dbConnection)
dbConnection.close()


# Adding the available quantity column to softone df
dfs1['Avail'] = dfs1['QTY1'] - dfs1['RSRVD']

# B2B connection and query
sqlEngine2      = create_engine('mysql+pymysql://elast:replace_with_working_pass@demohost.com', pool_recycle=3600)
dbConnection2   = sqlEngine2.connect()
dfb2b           = pd.read_sql(" SELECT virtuemart_product_id, product_sku, product_in_stock, published FROM adhoc_gr_elast.vhy5i_virtuemart_products;                               ", dbConnection2)
dbConnection2.close()

dfb2bclean = dfb2b[['product_sku', 'virtuemart_product_id', 'product_in_stock']]
dfs1clean = dfs1[['CODE','Avail']]
dfcompare = pd.merge(dfs1clean, dfb2bclean, how='inner', left_on='CODE', right_on='product_sku')
# dfcompare['SQL'] = "UPDATE `adhoc_gr_elast`.`vhy5i_virtuemart_products` SET `product_in_stock` = \'" + dfcompare['Avail'] + "\' WHERE (`virtuemart_product_id` = \'" + dfcompare['virtuemart_product_id'] + "\');"
# dfcompare['virtuemart_product_id'] = dfcompare['virtuemart_product_id'].to_string()
#dfcompare['Avail'] = dfcompare['Avail'].to_string()
# dfcompare['SQL'] = dfcompare['virtuemart_product_id'] + " " + dfcompare['Avail']
# dfcompare[dfcompare.isna().any(axis=1)].to_csv( 'comparison.csv', sep=';', decimal=',', encoding='utf-8')
# .to_csv('item_diff.csv', sep=';', decimal=',', encoding='utf-8')

if dfcompare[dfcompare.Avail != dfcompare.product_in_stock].empty:
    print("No new changes")
else:
    print("New item changes to apply!")
    dftoexport = dfcompare[dfcompare.Avail != dfcompare.product_in_stock]
    dftoexport[['Avail', 'virtuemart_product_id']].to_csv('item_diff.csv', sep=';', decimal=',', encoding='utf-8')


# print(dfcompare[['Avail', 'virtuemart_product_id']])
# .to_csv('items.csv', sep=';', decimal=',', encoding='utf-8')
print(dfcompare[dfcompare.Avail != dfcompare.product_in_stock])
# dfcompare[dfcompare.Avail != dfcompare.product_in_stock].to_csv('item_diff.csv', sep=';', decimal=',', encoding='utf-8')
