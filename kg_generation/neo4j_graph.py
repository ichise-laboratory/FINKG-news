import re

from neo4j import GraphDatabase
from sys import platform

class Neo4jGraph:
    # init method
    def __init__(self):
        # See https://neo4j.com/developer/aura-connect-driver/ for Aura specific connection URL.
        scheme = "bolt"  # connecting to Aura. use the "neo4j+s" URI scheme
        host_name = "localhost"

        """
        host: neo4j://localhost:7687
        user: neo4j
        password: nedo
        """
        # user = "russell3000"
        user = "neo4j"
        password = "finkg v2"
        port = 7687
        database = "finkg-news"
        # database = "finkg-testing" # use this for testing

        # different os use different neo4j port
        if platform == "linux" or platform == "linux2":
            print(platform)
            password = "nedo"
            port = 7687
            # linux
        elif platform == "darwin":
            print(platform)
            # OS X
        elif platform == "win32":
            print(platform)

        url = "{scheme}://{host_name}:{port}".format(
            scheme=scheme, host_name=host_name, port=port)

        print("url:",url)

        self.driver = GraphDatabase.driver(url, database=database, auth=(user, password))
        
    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    def remove_relationships_nodes(self):
        with self.driver.session() as session:
            session.execute_write(self._remove_relationships_nodes)

    @staticmethod
    def _remove_relationships_nodes(tx):
        # query string
        query = (
            "MATCH (n)-[r]->(m) DELETE r,n,m "
        )
        result = tx.run(query)
        return result

    # remove the existing nodes
    def remove_nodes(self):
        with self.driver.session() as session:
            session.execute_write(self._remove_nodes)

    @staticmethod
    def _remove_nodes(tx):

        query = (
            "MATCH (n) DELETE n"
        )
        result = tx.run(query)
        return result

    @staticmethod
    def _create_return_node(tx, entity):

        # get entity name
        for entityName, properties in entity.items():
            
            # loop through property pair
            for propertyPair in properties:

                # define neo4j sql
                sql = r"CREATE (e:" + entityName + "{"

                # get property
                for i, property in enumerate(propertyPair.items()):

                    if i > 0:
                        sql += ","

                    # get property and value
                    propertyName = property[0]
                    propertyValue = property[1]
                    if not propertyValue:
                        propertyValue = ''
                    print(f"propertyName: {propertyName}, propertyValue: {propertyValue}")
                    sql += propertyName + ':"' + propertyValue + '"'
                
                # end the sql
                sql += "})"
                print(sql)

                query = (sql)
                result = tx.run(query)

            return "Nodes have been created seccussfully."

    @staticmethod
    def _create_return_triple(tx, sql):
        print(sql)
        query = (sql)
        result = tx.run(query)

        return "Triples have been created seccussfully."

    # create nodes
    def createNodes(self, entity):
        with self.driver.session() as session:
            createNodeResult = session.execute_write(self._create_return_node, entity)
            print(createNodeResult)

    @staticmethod
    def _find_subject(self, entitySql):
        with self.driver.session() as session:

            result = session.read_transaction(self._find_return_subject, entitySql)

            for record in result:

                if record > 0:
                    return True
                else:
                    return False

    @staticmethod
    def _find_return_subject(tx, entitySql):
        sql = "match " + entitySql + " return count(s) as size"
        # execute query
        result = tx.run(sql)
        return [record['size'] for record in result]

    @staticmethod
    def _find_object(self, entitySql):
        with self.driver.session() as session:

            result = session.read_transaction(self._find_return_object, entitySql)

            for record in result:

                if record > 0:
                    return True
                else:
                    return False

    @staticmethod
    def _find_return_object(tx, entitySql):
        sql = "match " + entitySql + " return count(o) as size"
        # execute query
        result = tx.run(sql)
        return [record['size'] for record in result]

    @staticmethod
    def _find_triple(self, entitySql):
        with self.driver.session() as session:

            result = session.read_transaction(self._find_return_triple, entitySql)

            for record in result:

                if record > 0:
                    return True
                else:
                    return False

    @staticmethod
    def _find_return_triple(tx, entitySql):
        sql = "match " + entitySql + " return count(r) as size"
        # execute query
        result = tx.run(sql)
        return [record['size'] for record in result]

    @staticmethod
    def _find_return_mainCompany(tx, mainCompany):

        # set mainCompany
        for mainCompanyName, mainCompanyProperties in mainCompany.items():

            # mainCompany sql
            mainCompanySql = r"(s:" + mainCompanyName + "{"
            # get property
            for i, property in enumerate(mainCompanyProperties.items()):

                # get property and value
                propertyName = property[0]
                propertyValue = property[1]
                if propertyName == 'cik':
                    print(f"propertyName: {propertyName}, propertyValue: {propertyValue}")
                    mainCompanySql += propertyName + ':"' + propertyValue + '"'
                    break
            # end the sql
            mainCompanySql += "})"
            print(mainCompanySql)

            sql = "match " + mainCompanySql + " return count(s) as size"
            # execute query
            result = tx.run(sql)
            return [record['size'] for record in result]

    @staticmethod
    def _find_mainCompany(self, mainCompany):
        with self.driver.session() as session:

            result = session.read_transaction(self._find_return_mainCompany, mainCompany)

            for record in result:

                if record > 0:
                    return True
                else:
                    return False

    # get main subject sql
    def getMainCompanySql(self, mainCompany):

                # set mainCompany
        for mainCompanyName, mainCompanyProperties in mainCompany.items():

            # mainCompany sql
            matchMainCompanySql = r"match (s:" + mainCompanyName + "{"
            # get property
            for i, property in enumerate(mainCompanyProperties.items()):

                # get property and value
                propertyName = property[0]
                propertyValue = property[1]
                if propertyName == 'cik':
                    print(f"propertyName: {propertyName}, propertyValue: {propertyValue}")
                    matchMainCompanySql += propertyName + ':"' + propertyValue + '"'
                    break
            # end the sql
            matchMainCompanySql += "})"
            print(matchMainCompanySql)

        # set mainCompany
        for mainCompanyName, mainCompanyProperties in mainCompany.items():

            # mainCompany sql
            mainCompanySql = r" set "
            # get property
            for i, property in enumerate(mainCompanyProperties.items()):

                if i > 0:
                    mainCompanySql += ", "

                # get property and value
                propertyName = property[0]
                propertyValue = property[1]
                if not propertyValue:
                    propertyValue = ''
                # convert special char in neo4j
                if propertyName == 'name' or propertyName == 'wikipediaPage':
                    # convert special char in neo4j
                    propertyValue = self.replaceSpecialChar(propertyValue)
                    print(propertyValue)

                print(f"propertyName: {propertyName}, propertyValue: {propertyValue}")
                mainCompanySql += "s." + propertyName + '="' + propertyValue + '"'
            
            # end the sql
            mainCompanySql += ""
            print(mainCompanySql)
        
        return matchMainCompanySql + mainCompanySql

    # if main company exists, then set other properties
    def setMainCompanyProperty(self, mainCompany):

        if self._find_mainCompany(self, mainCompany):
            mainCompanySql = self.getMainCompanySql(mainCompany)

            # neo4j session
            with self.driver.session() as session:
                # create triple
                session.execute_write(self._create_return_mainCompany, mainCompanySql=mainCompanySql)    

    @staticmethod
    def _create_return_mainCompany(tx, mainCompanySql):
        print(mainCompanySql)
        tx.run(mainCompanySql)

    # create subject-predicate-object
    def createTriple(self, subject, predicate, object):

        # neo4j session
        with self.driver.session() as session:

            subjectSql = self.getSubjectSql(subject)
            subjectFlg = self._find_subject(self, subjectSql)

            objectSql = self.getObjectSql(object)
            objectFlg = self._find_object(self, objectSql)

            predicateSql = self.getPredicateSql(predicate)
            tripleSql = subjectSql + predicateSql + objectSql
            tripleFlg = self._find_triple(self, tripleSql)

            if not subjectFlg and not objectFlg and not tripleFlg:
                # create triple
                session.execute_write(self._create_return_triple, tripleSql)

            elif subjectFlg and not objectFlg and not tripleFlg:
                # create triple
                session.execute_write(self._create_return_ot, subjectSql=subjectSql, predicateSql=predicateSql, objectSql=objectSql)

            elif subjectFlg and objectFlg and not tripleFlg:
                # create triple
                session.execute_write(self._create_return_t, subjectSql=subjectSql, predicateSql=predicateSql, objectSql=objectSql)

            elif not subjectFlg and objectFlg and not tripleFlg:
                # create triple
                session.execute_write(self._create_return_st, subjectSql=subjectSql, predicateSql=predicateSql, objectSql=objectSql)

    @staticmethod
    def _create_return_st(tx, subjectSql, predicateSql, objectSql):
        query = "match " + objectSql
        query += " create " + subjectSql + predicateSql + " (o) return count(r) as size"
        print(query)
        result = tx.run(query)

        for record in result:

            if record[0] > 0:
                return "Triples have been created seccussfully."
            else:
                return "Error has occurred when try to create triple."

    @staticmethod
    def _create_return_t(tx, subjectSql, predicateSql, objectSql):
        query = "match " + subjectSql + ", " + objectSql
        query += " create (s)" + predicateSql + "(o)" + " return count(r) as size"
        print(query)
        result = tx.run(query)

        for record in result:

            if record[0] > 0:
                return "Triples have been created seccussfully."
            else:
                return "Error has occurred when try to create triple."

    @staticmethod
    def _create_return_ot(tx, subjectSql, predicateSql, objectSql):
        query = "match " + subjectSql
        query += " create (s)" + predicateSql + objectSql + "return count(r) as size"
        print(query)
        result = tx.run(query)

        for record in result:

            if record[0] > 0:
                return "Triples have been created seccussfully."
            else:
                return "Error has occurred when try to create triple."

    @staticmethod
    def _create_return_triple(tx, tripleSql):
        query = "create " + tripleSql + "return count(r) as size"
        print(query)
        result = tx.run(query)

        for record in result:

            if record[0] > 0:
                return "Triples have been created seccussfully."
            else:
                return "Error has occurred when try to create triple."

    # get entity sql
    def getPredicateSql(self, predicate):
        print(type(predicate))

        if type(predicate) is dict:
            for predicateName, predicateProperties in predicate.items():

                # subject sql
                predicateSql = r"-[r:" + predicateName + "{"
                # get property
                for i, property in enumerate(predicateProperties.items()):

                    if i > 0:
                        predicateSql += ", "

                    # get property and value
                    propertyName = property[0]
                    propertyValue = property[1]
                    if not propertyValue:
                        propertyValue = ''
                    # convert special char in neo4j
                    if propertyName == 'securityName' or propertyName == 'positions' or propertyName== 'ownershipValue':
                        # convert special char in neo4j
                        propertyValue = self.replaceSpecialChar(propertyValue)
                        print(propertyValue)

                    print(f"propertyName: {propertyName}, propertyValue: {propertyValue}")
                    predicateSql += propertyName + ':"' + propertyValue + '"'
                predicateSql += "}]->"
            return predicateSql
        else:
            return f"-[r:{predicate}]->"

    # get subject sql
    def getSubjectSql(self, subject):

        # set subject
        for subjectName, subjectProperties in subject.items():

            # subject sql
            subjectsql = r"(s:" + subjectName + "{"
            # get property
            for i, property in enumerate(subjectProperties.items()):

                if i > 0:
                    subjectsql += ", "

                # get property and value
                propertyName = property[0]
                propertyValue = property[1]
                if not propertyValue:
                    propertyValue = ''
                # convert special char in neo4j
                if propertyName == 'name' or propertyName == 'wikipediaPage' or propertyName == 'mailingAddress':
                    # convert special char in neo4j
                    propertyValue = self.replaceSpecialChar(propertyValue)
                    print(propertyValue)

                print(f"propertyName: {propertyName}, propertyValue: {propertyValue}")
                subjectsql += propertyName + ':"' + propertyValue + '"'
            
            # end the sql
            subjectsql += "})"
            print(subjectsql)
        
        return subjectsql

    # get object sql
    def getObjectSql(self, object):

        # set object
        for objectName, objectProperties in object.items():

            # object sql
            objectsql = r"(o:" + objectName + "{"
            # get property
            for i, property in enumerate(objectProperties.items()):

                if i > 0:
                    objectsql += ", "

                # get property and value
                propertyName = property[0]
                propertyValue = property[1]
                if not propertyValue:
                    propertyValue = ''
                # convert special char in neo4j
                if propertyName == 'name':
                    # convert special char in neo4j
                    propertyValue = self.replaceSpecialChar(propertyValue)
                    print(propertyValue)

                print(f"propertyName: {propertyName}, propertyValue: {propertyValue}")
                objectsql += propertyName + ':"' + propertyValue + '"'
            
            # end the sql
            objectsql += "})"
            print(objectsql)
        
        return objectsql

    # replace special char
    def replaceSpecialChar(self, text):
        if not text:
            return ''

        matchWordList = ['\\\\','"']
        substitution = "\\\\"

        lRegexp = "["
        rRegexp = "]"

        for matchWord in matchWordList:

            regExp = lRegexp + matchWord + rRegexp

            substi = substitution + matchWord
            
            text = re.sub(regExp, substi,text)

            # print(text)

        return text
    
    @staticmethod
    def _remove_duplicated_nods(tx, label, property):
        query = (
            "MATCH (n:" + label + ") "
            "WITH n." + property + " AS prop, COLLECT(n) AS nodes "
            "WHERE SIZE(nodes) > 1 "
            "FOREACH (n IN TAIL(nodes) | DETACH DELETE n)"
        )
        tx.run(query)
    
    def remove_duplicated_nods(self, label, property):
        with self.driver.session() as session:
            session.execute_write(self._remove_duplicated_nods, label, property)

# main implement area
if __name__ == "__main__":

    # init graph
    graph = Neo4jGraph()

    # remove all relation and nodes
    # graph.remove_relationships_nodes()
    # graph.remove_nodes()
    print('All the existed relations and nodes have been removed.')
        
    # create a triple
    # graph.createTriple(subject='Company', subjectName="BJ'S WHOLESALE CLUB HOLDINGS", predicate='has_ticker', object='Ticker', objectName='BJ')