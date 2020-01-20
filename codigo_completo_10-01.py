output_pc = 'C:/Users/Caio/Desktop/coletar_dados/pc67'
output_sb = 'C:/Users/Caio/Desktop/coletar_dados/sb67'
output_me = 'C:/Users/Caio/Desktop/coletar_dados/me67'
output_me_select = 'C:/Users/Caio/Desktop/coletar_dados/meselect67'
output_sb_select = 'C:/Users/Caio/Desktop/coletar_dados/sbselect67'
output_pc_select = 'C:/Users/Caio/Desktop/coletar_dados/pcselect67'
output_line = 'C:/Users/Caio/Desktop/coletar_dados/line67'
output_merge = 'C:/Users/Caio/Desktop/coletar_dados/merge67'
output_sb_ruido = 'C:/Users/Caio/Desktop/coletar_dados/sbruido67'
poly = 'crater67_dddfeb8e_b234_4355_9311_0a4b36c186f7'
dem = 'Pluto_NewHorizons_Global_DEM_300m_Jul2017_16bit_56f84df1_5b7b_4623_acdc_f46a6df5f5e8'
slope = 'golbal_slope_a29925db_30fe_44b9_9b52_b51a5c166bf3' 

a = processing.run("qgis:fieldcalculator", {'INPUT':poly,'FIELD_NAME':'1.3-field','FIELD_TYPE':0,'FIELD_LENGTH':10,'FIELD_PRECISION':3,'NEW_FIELD':True,'FORMULA':'((length(shortest_line(centroid($geometry),boundary($geometry)))))*1.3','OUTPUT':'memory:'})
b = processing.run("saga:polygoncentroids", {'POLYGONS':a['OUTPUT'],'METHOD         ':True,'CENTROIDS':'TEMPORARY_OUTPUT'})
c = processing.run("saga:variabledistancebuffer", {'SHAPES':b['CENTROIDS'],'DIST_FIELD':'1.3-field','DIST_SCALE':1,'NZONES':1,'DARC':5,'DISSOLVE       ':True,'POLY_INNER       ':False,'BUFFER':'TEMPORARY_OUTPUT'})
d = processing.run("native:polygonstolines", {'INPUT':c['BUFFER'],'OUTPUT':'TEMPORARY_OUTPUT'})
e = processing.run("native:densifygeometriesgivenaninterval", {'INPUT':d['OUTPUT'],'INTERVAL':600,'OUTPUT':'TEMPORARY_OUTPUT'})
f = processing.run("native:extractvertices", {'INPUT':e['OUTPUT'],'OUTPUT':'TEMPORARY_OUTPUT'})
g = processing.run("qgis:exportaddgeometrycolumns", {'INPUT':f['OUTPUT'],'CALC_METHOD':0,'OUTPUT':'TEMPORARY_OUTPUT'})
h = processing.run("qgis:exportaddgeometrycolumns", {'INPUT':b['CENTROIDS'],'CALC_METHOD':0,'OUTPUT':'TEMPORARY_OUTPUT'})
h2 = processing.run("qgis:fieldcalculator", {'INPUT':h['OUTPUT'],'FIELD_NAME':'ID','FIELD_TYPE':0,'FIELD_LENGTH':10,'FIELD_PRECISION':3,'NEW_FIELD':True,'FORMULA':'0','OUTPUT':'memory:'})
i = processing.run("native:joinattributestable", {'INPUT':g['OUTPUT'],'FIELD':'ID','INPUT_2':h2['OUTPUT'],'FIELD_2':'ID','FIELDS_TO_COPY':[],'METHOD':1,'DISCARD_NONMATCHING':False,'PREFIX':'','OUTPUT':'TEMPORARY_OUTPUT'})
j = processing.run("shapetools:xy2line", {'InputLayer':i['OUTPUT'],'InputCRS':QgsCoordinateReferenceSystem('USER:100000'),'OutputCRS':QgsCoordinateReferenceSystem('USER:100000'),'LineType':0,'StartUseLayerGeom':False,'StartXField':'xcoord_2','StartYField':'ycoord_2','EndUseLayerGeom':False,'EndXField':'xcoord','EndYField':'ycoord','ShowStartPoint':True,'ShowEndPoint':True,'DateLineBreak':False,'OutputLineLayer':'TEMPORARY_OUTPUT','OutputPointLayer':'TEMPORARY_OUTPUT'})
k = processing.run("saga:profilesfromlines", {'DEM':dem,'VALUES':'','LINES':j['OutputLineLayer'],'NAME':'fid','SPLIT         ':False,'PROFILE':'TEMPORARY_OUTPUT','PROFILES':'TEMPORARY_OUTPUT'})
l = processing.run("saga:addrastervaluestopoints", {'SHAPES':k['PROFILE'],'GRIDS':slope,'RESAMPLING':0,'RESULT':'TEMPORARY_OUTPUT'})

layer = QgsVectorLayer(l['RESULT'])
QgsProject.instance().addMapLayer(layer)

#slope break

#cria uma dicionario com as linhas_ID(key) e os valores do slope 

from collections import defaultdict
#processing.runandload("qgis:intersection", layer1, layer2, "memory:myLayerName")
#layer = QgsMapLayerRegistry.instance().mapLayersByName("memory:myLayerName")[0]

all_features = layer.getFeatures()
all_features2 = layer.getFeatures()

lista_repetition = []
for alllineids in all_features2:
    lista_repetition.append(alllineids['LINE_ID'])
repetition = max(lista_repetition)

value = layer.fields().indexFromName('Declividade')
key = layer.fields().indexFromName('LINE_ID')
declive = layer.fields().indexFromName('Z')
x = 1
layer.startEditing()
lista_values2 = []
lista_values = []
lista_key = []
for feature in all_features:
    if feature['ID'] == x:
        x = x + 1
        declives = feature.attributes()[declive]
        slope = feature.attributes()[value]
        line = feature.attributes()[key]
        lista_values.append(slope)
        lista_values2.append(declives)
        lista_key.append(line)
values_values2 = []
for x in zip(lista_values, lista_values2):
    values_values2.append(list(x))

dic= defaultdict(list)
for i,j in zip(lista_key,values_values2):
    dic[i].append(j)
#print(dic)
# seleciona os valores de acordo com a regra (slope break)
values_SB = []
keys=[]
for c,listas in dic.items():
    try:
        for i in range(len(listas)):
            if listas[i][0] >= 8 and listas[i+1][0] <= 8:
                if listas[i][1] < listas[i+1][1]:
                    values_SB.append(listas[i+1][0])
                    keys.append(c)
    except IndexError:
        pass
print(values_SB)
#print(keys)
# selecionar as features 

strvalue=list(map(str,values_SB))
strkey=list(map(str,keys))
k=0
v=0

for item in keys:
    listk = strkey[k]
    listv = strvalue[v]
    layer.selectByExpression('\"LINE_ID\" IN ('+listk+') AND \"Declividade\" IN ('+listv+')', QgsVectorLayer.AddToSelection)
    v=v+1
    k=k+1
    
#extrair selected slope break
m0 = processing.run("native:saveselectedfeatures", {'INPUT':layer,'OUTPUT':output_sb_ruido})
layer_sb = QgsVectorLayer(m0['OUTPUT'])
m01 = processing.run("qgis:selectbyexpression", {'INPUT':layer_sb,'EXPRESSION':'\"fid\"= maximum (\"fid\",\"LINE_ID\")','METHOD':0})
m = processing.run("native:saveselectedfeatures", {'INPUT':layer_sb,'OUTPUT':output_sb})
#Maximum Elevation
##retirar a selecao anterior?
n = processing.run("qgis:selectbyexpression", {'INPUT':layer,'EXPRESSION':'\"Z\" = maximum(\"z\",\"LINE_ID\")','METHOD':0})
n2 = processing.run("native:saveselectedfeatures", {'INPUT':layer,'OUTPUT':output_me})
layer.removeSelection()
#add layers to map 
layer2 = QgsVectorLayer(m['OUTPUT'])
QgsProject.instance().addMapLayer(layer2)

layer3 = QgsVectorLayer(n2['OUTPUT'])
QgsProject.instance().addMapLayer(layer3)

#Delineation
layer1 = layer2
layer2 = layer3
layer3 = layer
layer1.startEditing()
layer2.startEditing()
layer3.startEditing()
idx1 = layer2.fields().indexFromName('LINE_ID')
u1 = layer2.minimumValue(idx1)
processing.run("qgis:selectbyexpression", {'INPUT':layer2,'EXPRESSION':'\"fid\"= maximum (\"fid\",\"LINE_ID\") AND \"LINE_ID\" = {}'.format(u1),'METHOD':0})
selected_features = layer2.selectedFeatures()
for point in selected_features:
    u2 = point['fid']
print(u1)
print(u2)
exp_me0=QgsExpression("\"LINE_ID\"='{}'AND\"fid\"='{}'".format(u1,u2))
feature_me= layer2.getFeatures(QgsFeatureRequest(exp_me0))
x=u1
lista =list(map(str, range(repetition+1)))
listlayer1=[]
listlayer2=[]
listlayer3=[]
for f in feature_me:
    geom_me0= f.geometry()
for times in range(repetition+1):
    x=x+1
    print('for1')
    print(x)
    y=0
    try:
        lineid= lista[x]
    except IndexError:
        continue
    exp_me = QgsExpression('\"LINE_ID\" = ('+lineid+')')
    exp_sb_2 = QgsExpression('\"LINE_ID\" = ('+lineid+')')
    exp_control = QgsExpression('\"LINE_ID\" = ('+lineid+')')
    feature_me=layer2.getFeatures(QgsFeatureRequest(exp_me))
    feature_sb_2 = layer1.getFeatures(QgsFeatureRequest(exp_sb_2))
    feature_control = layer3.getFeatures(QgsFeatureRequest(exp_control))
    layer1.selectByExpression('\"LINE_ID\" = ('+lineid+')')
    numb_features_SB = layer1.selectedFeatureCount()
    layer1.removeSelection()
    if  numb_features_SB != 0:
        for f2 in feature_sb_2:
            layer1.selectByExpression('\"LINE_ID\" = ('+lineid+')')
            numb_features_SB = layer1.selectedFeatureCount()
            layer1.removeSelection()
            geom_sb_2 = f2.geometry()
            dist = geom_me0.distance(geom_sb_2)
            y=y+1
            #print("y{}".format(y))
            #print('numb_sb{}'.format( numb_features_SB))
            if dist < 1000 and numb_features_SB != 0:
                geom_me0 = f2.geometry()
                print('sb')
                print(f2['LINE_ID'])
                print(f2['ID'])
                selectedlayer1= f2['ID']
                listlayer1.append(selectedlayer1)
            else:
                if y == numb_features_SB or numb_features_SB == 0:
                    for f_me in feature_me:
                        geom_me = f_me.geometry()
                        dist2 = geom_me0.distance(geom_me)
                        print('forme')
                        #print(f_me['ID'])
                        #print(lineid)
                        if dist2 <1000:
                            geom_me0 = geom_me
                            print('me')
                            print(f_me['LINE_ID'])
                            print(f_me['ID'])
                            layer2.select(f_me.id())
                            break
                        else:
                            list_id_key = []
                            list_dist_value = []
                            list2_id_key = []
                            list2_dist_value = []
                            for f_control in feature_control:
                                geom_control = f_control.geometry()
                                dist3 = geom_me0.distance(geom_control)
                                list_id_key.append(f_control['ID'])
                                list_dist_value.append(dist3)
                                keys = list_id_key
                                values = list_dist_value
                                dictionary = dict(zip(keys, values))
                                dictionary2 = dict(zip(keys, values))
                            list_pcid = []
                            for times in range(3):
                                min_val = min(dictionary.values())
                                for k, v in dictionary.items():
                                    if v == min_val:
                                        list_pcid.append(k)
                                        del dictionary[k]
                                        break
                            lista2 =list(map(str,list_pcid))
                            y= 0
                            for times in range(3):
                                lineid2= lista2[y]
                                exp_control2 = QgsExpression('\"ID\" = ('+lineid2+') ')
                                feature_pcid1 = layer3.getFeatures(QgsFeatureRequest(exp_control2))
                                y=y+1
                                for f_pcid1 in feature_pcid1:
                                    feature_pcid1_geom = f_pcid1.geometry()
                                    dist4 = geom_me.distance(feature_pcid1_geom)
                                    list2_id_key.append(f_pcid1['ID'])
                                    list2_dist_value.append(dist4)
                            ke = list2_id_key
                            va = list2_dist_value
                            dictionary_dist = dict(zip(ke, va))
                            min_val2 = min(dictionary_dist.values())
                            for ky, vs in dictionary_dist.items():
                                if vs == min_val2:
                                    new_select_pcid = ky
                            pc_slect_str = str(new_select_pcid)
                            exp_control3 = QgsExpression('\"ID\" = ('+pc_slect_str+') ')
                            feature_pcid2 = layer3.getFeatures(QgsFeatureRequest(exp_control3))
                            for pc_feature in feature_pcid2:
                                geom_me0 = pc_feature.geometry()
                                print('pc1')
                                print(pc_feature['LINE_ID'])
                                print(pc_feature['ID'])
                                #print(list_pcid)
                                #print(dictionary_dist)
                                #print(new_select_pcid)
                            layer3.selectByExpression('\"ID\" IN ('+pc_slect_str+')', QgsVectorLayer.AddToSelection)
                        break
    else:   
        for f_me in feature_me:
            geom_me = f_me.geometry()
            dist2 = geom_me0.distance(geom_me)
            #print(dist2)
            #print(f_me['ID'])
            #print(lineid)
            if dist2 <1000:
                geom_me0 = geom_me
                print('me2')
                print(f_me['LINE_ID'])
                print(f_me['ID'])
                layer2.select(f_me.id())
                break
            else:
                list_id_key = []
                list_dist_value = []
                list2_id_key = []
                list2_dist_value = []
                for f_control in feature_control:
                    geom_control = f_control.geometry()
                    dist3 = geom_me0.distance(geom_control)
                    list_id_key.append(f_control['ID'])
                    list_dist_value.append(dist3)
                    keys = list_id_key
                    values = list_dist_value
                    dictionary = dict(zip(keys, values))
                    dictionary2 = dict(zip(keys, values))
                list_pcid = []
                for times in range(3):
                    min_val = min(dictionary.values())
                    for k, v in dictionary.items():
                        if v == min_val:
                            list_pcid.append(k)
                            del dictionary[k]
                            break
                lista2 =list(map(str,list_pcid))
                y= 0
                for times in range(3):
                    lineid2= lista2[y]
                    exp_control2 = QgsExpression('\"ID\" = ('+lineid2+') ')
                    feature_pcid1 = layer3.getFeatures(QgsFeatureRequest(exp_control2))
                    y=y+1
                    for f_pcid1 in feature_pcid1:
                        feature_pcid1_geom = f_pcid1.geometry()
                        dist4 = geom_me.distance(feature_pcid1_geom)
                        list2_id_key.append(f_pcid1['ID'])
                        list2_dist_value.append(dist4)
                ke = list2_id_key
                va = list2_dist_value
                dictionary_dist = dict(zip(ke, va))
                min_val2 = min(dictionary_dist.values())
                for ky, vs in dictionary_dist.items():
                    if vs == min_val2:
                        new_select_pcid = ky
                pc_slect_str = str(new_select_pcid)
                exp_control3 = QgsExpression('\"ID\" = ('+pc_slect_str+') ')
                feature_pcid2 = layer3.getFeatures(QgsFeatureRequest(exp_control3))
                for pc_feature in feature_pcid2:
                    geom_me0 = pc_feature.geometry()
                    print('pc2')
                    print(pc_feature['LINE_ID'])
                    print(pc_feature['ID'])
                    #print(list_pcid)
                    #print(dictionary_dist)
                    #print(new_select_pcid)
                layer3.selectByExpression('\"ID\" IN ('+pc_slect_str+')', QgsVectorLayer.AddToSelection)
            break
listtostr=list(map(str,listlayer1))
p = 0
for feature in listlayer1:
    pointtoselect = listtostr[p]
    layer1.selectByExpression('\"ID\" IN ('+pointtoselect+')', QgsVectorLayer.AddToSelection)
    p=p+1
    
o = processing.run("native:saveselectedfeatures", {'INPUT':layer3,'OUTPUT':output_pc_select})
o1 = processing.run("native:saveselectedfeatures", {'INPUT':layer1,'OUTPUT':output_sb_select})
o2 = processing.run("native:saveselectedfeatures", {'INPUT':layer2,'OUTPUT':output_me_select})

layer_pc_select = QgsVectorLayer(o['OUTPUT'])
####QgsProject.instance().addMapLayer(layer_pc_select)
layer_sb_select = QgsVectorLayer(o1['OUTPUT'])
####QgsProject.instance().addMapLayer(layer_sb_select)
layer_me_select = QgsVectorLayer(o2['OUTPUT'])
####QgsProject.instance().addMapLayer(layer_me_select)
# merge 
p = processing.run("native:mergevectorlayers", {'LAYERS':[layer_pc_select,layer_me_select,layer_sb_select],'CRS':None,'OUTPUT':output_merge})
# create line delineation 
q = processing.run("qgis:pointstopath", {'INPUT':p['OUTPUT'],'ORDER_FIELD':'LINE_ID','GROUP_FIELD':None,'DATE_FORMAT':'','OUTPUT':output_line})

# altura
import statistics
layer_points = QgsVectorLayer(p['OUTPUT'])
feature_points= layer_points.getFeatures()

list_altura = []
for alturas in feature_points:
    list_altura.append(alturas['Z'])

features_selected = layer_points.selectAll()
numb_feature = layer_points.selectedFeatureCount()
layer_points.removeSelection()
soma = sum(list_altura)
media_altura = soma/(numb_feature)
#print(media_altura)
variacao_altura = statistics.stdev(list_altura)
print (variacao_altura)

#profundidade 
layer_all= QgsVectorLayer(l['RESULT'])
feature_all= layer_all.getFeatures()
list_zmin = []
#index=layer_all.fields().indexFromName('Z')
for z in feature_all:
    list_zmin.append(z['Z'])

profundidade = media_altura - min(list_zmin)
print (profundidade) 

# raio 
layer_centroid=QgsVectorLayer(b['CENTROIDS'])
feature_points= layer_points.getFeatures()
feature_centroid= layer_centroid.getFeatures()
list_radious = []
for centroid in feature_centroid:
    geom_centrois = centroid.geometry()
for points in feature_points:
    geom_points = points.geometry()
    dist = geom_centrois.distance(geom_points)
    list_radious.append(dist)
features_selected = layer_points.selectAll()
numb_feature = layer_points.selectedFeatureCount()
layer_points.removeSelection()
soma = sum(list_radious)
diametro = soma*2
media_diametro = diametro/(numb_feature)

print(media_diametro)

