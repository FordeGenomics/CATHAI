from flask import url_for
from wtforms.fields import Field
from wtforms.widgets import HiddenInput
from wtforms.compat import text_type
import pandas as pd
import os, subprocess


class Operations:
    def restart_shiny():
        subprocess.run(['/usr/bin/sudo', '/usr/bin/systemctl', 'restart', 'shiny-server.service'])

    # def restart_cathai():
    #     subprocess.run(['/usr/bin/sudo', '/usr/bin/systemctl', 'restart', 'cathai.service'])


class Metadata:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.updateSamples()
        self.updateClusters()
        self.updateSamplesClusters()

    def updateSamples(self):
        samples, species, STs, clusterSpecies, clusterSTs = Metadata.processSamples(self.data_dir)
        self.samples = samples
        self.species = species
        self.STs = STs
        self.clusterSpecies = clusterSpecies
        self.clusterSTs = clusterSTs

    def updateClusters(self):
        self._clusters = Metadata.getClusters(self.data_dir)

    def updateSamplesClusters(self):
        samples = self.samples
        samples['Clusters'] = [self.getSampleClusters(x) for x in samples['Sample ID'].values.tolist()]
        self.samples = samples

    def __repr__(self):
        return self._clusters
    
    @property
    def samples(self):
        return self._samples
    
    @property
    def species(self):
        return self._species

    @property
    def STs(self):
        return self._STs

    @property
    def clusterSpecies(self):
        return self._clusterSpecies

    @property
    def clusterSTs(self):
        return self._clusterSTs

    @property
    def clusters(self):
        return self._clusters

    @samples.setter
    def samples(self, value):
        self._samples = value
    
    @species.setter
    def species(self, value):
        self._species = value

    @STs.setter
    def STs(self, value):
        self._STs = value

    @clusterSpecies.setter
    def clusterSpecies(self, value):
        self._clusterSpecies = value

    @clusterSTs.setter
    def clusterSTs(self, value):
        self._clusterSTs = value

    @clusters.setter
    def clusters(self, value):
        self._clusters = value
        self.saveClusters()

    def validateSpecies(self, species):
        return species in self.species

    def validateST(self, species, st):
        validSTs = self.getSpeciesSTs(species)
        return st in validSTs

    def validateCluster(self, species, st, members):
        validMembers = self.getSTSMembers(species, st)
        ret = True
        for member in members:
            if member not in validMembers['Sample ID']:
                ret = False
        return ret

    def existingClusterName(self, name):
        return name in self._clusters['CLUSTER'].values.tolist()

    def getSpeciesSTs(self, species, clusterable=False):
        if species not in self._STs.keys():
            return "NA"
        elif clusterable:
            return self._clusterSTs[species]
        else:
            return self._STs[species]

    def getSTSMembers(self, species, ST, asDict=True):
        speciesMembers = self.samples.loc[self.samples['Species'].str.strip() == species]
        STSMembers = speciesMembers.loc[speciesMembers['MLST (ST)'] == ST]
        STSMembers.index = STSMembers['Sample ID']
        if asDict:
            return STSMembers.to_dict()
        else:
            return STSMembers
    
    def getCluster(self, cluster, asDict=True):
        cluster = self._clusters.loc[self._clusters['CLUSTER'] == cluster]
        if len(cluster) != 1:
            return None
        if asDict:
            return cluster.iloc[0].to_dict()
        else:
            return cluster.iloc[0]

    def getICluster(self, i, asDict=True):
        try:
            cluster = self._clusters.iloc[int(i)]
        except:
            return None
        if asDict:
            return cluster.to_dict()
        else:
            return cluster

    def getSampleClusters(self, sample):
        ret = []
        for i, v in self._clusters.iterrows():
            if sample in v['MEMBERS'].split(';'):
                ret.append(v['CLUSTER'])
        return ', '.join(ret)

    def getSample(self, sample, asDict=True):
        ret = self.samples.loc[self.samples['Sample ID'] == sample]
        if len(ret) < 1:
            assert ValueError(f"Sample not found: {sample}")
        if len(ret) > 1:
            assert ValueError(f"Multiple entries found for sample: {sample}")
        ret.index = ret['Sample ID']
        if asDict:
            return ret.to_dict()
        else:
            return ret
        
    def processSamples(distDir):
        samples = Metadata.getSamples(distDir)
        for i, row in samples.iterrows():
            if not str(row['MLST (ST)']).isnumeric():
                row['MLST (ST)'] = 'NA'
        species = list(set([x.strip() for x in samples['Species'].values.tolist()]))
        species.sort()
        STs={}
        clusterSpecies=[]
        clusterSTs={}
        for specie in species:
            clusterable=False
            clusterableSTs=[]
            sts = samples.loc[samples['Species'].str.strip() == specie]['MLST (ST)'].values.tolist()
            sts = list(set(sts))
            sts.sort()
            STs[specie] = sts
            for st in sts:
                speciesMembers = samples.loc[samples['Species'].str.strip() == specie]
                STSMembers = speciesMembers.loc[speciesMembers['MLST (ST)'] == st]
                if len(STSMembers) > 1:
                    clusterable = True
                    clusterableSTs.append(st)
            if clusterable:
                clusterSpecies.append(specie)
                clusterSTs[specie] = clusterableSTs
        return samples, species, STs, clusterSpecies, clusterSTs

    def getLatestDir(distDir):
        data_dirs = []
        for d in sorted(os.listdir(distDir), reverse=True):
            bd = os.path.join(distDir, d)
            if os.path.isdir(bd):
                date = os.path.basename(bd)
                data_dirs.append(date)
        if len(data_dirs) == 0:
            return '.'
        else:
            return str(max(data_dirs, key=os.path.basename))

    def getSamples(distDir):
        latest_data = Metadata.getLatestDir(distDir)
        try:
            df = pd.read_csv(f"{distDir}/{latest_data}/metadata.csv", dtype=str, keep_default_na=False)
        except:
            df = pd.DataFrame()
            df['Species'] = ''
            df['Sample ID'] = ''
            df['MLST (ST)'] = ''
        return df

    def getClusters(distDir):
        try:
            df = pd.read_csv(f"{distDir}/clusters.csv", keep_default_na=False)
        except:
            df = pd.DataFrame()
        return df

    def getDistances(self, species, st, asJSON=True):
        distDir = self.data_dir
        latest_data = Metadata.getLatestDir(distDir)
        fspecies = species.replace(' ', '_')
        if st.isnumeric():
            fst = f"ST{st}"
        else:
            fst = "ST_NA"
        filename = '_'.join([fspecies, fst]) + ".snpDists"
        try:
            df = pd.read_csv(f"{distDir}/{latest_data}/{filename}", sep='\t', index_col=0)
            if len(df.columns) == 0:
                df = pd.read_csv(f"{distDir}/{latest_data}/{filename}", sep=',', index_col=0)
        except:
            STSMembers = self.getSTSMembers(species, st, asDict=False)
            df = pd.DataFrame(columns=STSMembers['Sample ID'], index=STSMembers['Sample ID'])
            df = df.fillna("Not Processed")
        if asJSON:
            return df.to_json()
        else:
            return df

    def saveClusters(self):
        distDir = self.data_dir
        return self._clusters.to_csv(f"{distDir}/clusters.csv", index=False)

###########################################################

def register_template_utils(app):
    """Register Jinja 2 helpers (called from __init__.py)."""

    @app.template_test()
    def equalto(value, other):
        return value == other

    @app.template_global()
    def is_hidden_field(field):
        from wtforms.fields import HiddenField
        return isinstance(field, HiddenField)

    app.add_template_global(index_for_role)


def index_for_role(role):
    return url_for(role.index)

###########################################################

class CustomSelectField(Field):
    widget = HiddenInput()

    def __init__(self, label='', validators=None, multiple=False,
                 choices=[], allow_custom=True, **kwargs):
        super(CustomSelectField, self).__init__(label, validators, **kwargs)
        self.multiple = multiple
        self.choices = choices
        self.allow_custom = allow_custom

    def _value(self):
        return text_type(self.data) if self.data is not None else ''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[1]
            self.raw_data = [valuelist[1]]
        else:
            self.data = ''
