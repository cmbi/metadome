metadom-api is a REST wrapper around metadom.

# metadom-api
## Development
Under construction

## Endpoints
| HTTP | Method URI | Action | Output type |
| :---: | :---: | :---: | :---: | 
| GET | http://[hostname]/metadom/api/chromosome/[locus] | Retrieve a list of loci that are aligned via meta-domain relation to this locus |  |
| GET | http://[hostname]/metadom/api/gene/[gene name] | Retrieve a list of loci that are aligned via meta-domain relation to this locus |	<code>{ <br/><indent>	protein: [<protein>], domain	} <code/>|
| GET | http://[hostname]/metadom/api/gene/[gene name]/[cDNA position] | Retrieve a list of loci that are aligned via meta-domain relation to this locus |	<code>{ <br/><indent>	protein: [<protein>], domain	} <code/>|
| GET | http://[hostname]/metadom/api/protein/[swiss-prot id] | Retrieve a list of loci that are aligned via meta-domain relation to this locus |	<code>{ <br/><indent>	protein: [<protein>], domain	} <code/>|
| GET | http://[hostname]/metadom/api/protein/[swiss-prot id]/[protein position] | Retrieve a list of loci that are aligned via meta-domain relation to this locus |	<code>{ <br/><indent>	protein: [<protein>], domain	} <code/>|
| GET | http://[hostname]/metadom/api/domain/[Pfam id] | Retrieve a list of loci that are aligned via meta-domain relation to this locus |	<code>{ <br/><indent>	protein: [<protein>], domain	} <code/>|
| GET | http://[hostname]/metadom/api/domain/[Pfam id]/[domain position] | Retrieve a list of loci that are aligned via meta-domain relation to this locus |	<code>{ <br/><indent>	protein: [<protein>], domain	} <code/>|

### Output
| Output type | Output |
| :---: | :--- |
| Mapping | <pre>{ <br>&nbsp; proteins: <br>&nbsp;&nbsp;[<br>&nbsp;&nbsp;&nbsp; protein*, ... <br>&nbsp;&nbsp;], domain <br>} <pre/> |
| protein | <pre>{ <br>&nbsp; swiss-prot id: <br>&nbsp;&nbsp;[<br>&nbsp;&nbsp;&nbsp; protein*, ... <br>&nbsp;&nbsp;], domain	} <pre/> |

\*: zero or many and \+: one or many
