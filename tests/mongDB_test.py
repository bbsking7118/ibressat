import pymongo
import  xlrd
import  datetime

client = pymongo.MongoClient("mongodb+srv://bbsking:taelim5612@cluster0.2vmwy97.mongodb.net/?retryWrites=true&w=majority")
mydb = client["test_database"]
mycol = mydb["test_collection"]

company = "LG"
database = "20210310"
class Mongdb_test():
    def company_base(self,company,database):
        mydb = client[database]
        mycol = mydb[company + "(기본정보)"]

        workbook = xlrd.open_workbook(company + '_기본정보.xls',encoding_override="cp949")
        worksheet = workbook.sheet_by_index(0)

        data ={}
        for col in range(11):
            name = worksheet.cell_value(0,col)
            if name == "종목명":
                name = "_id"
            value = worksheet.cell_value(1,col)
            data.update({name:value})
        #print(data)
        mycol.delete_many({})
        mycol.insert_one(data)
        for i in mycol.find():
            print(i)
        pass
    def conpany_tickvalue(self):
        pass

Mongdb_test().company_base(company = company, database = database)