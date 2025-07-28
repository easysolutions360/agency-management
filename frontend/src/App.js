import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Move FormInput component outside to prevent recreation on every render
const FormInput = ({ label, type = "text", value, onChange, required = true, options = null }) => (
  <div className="mb-4">
    <label className="block text-sm font-medium text-gray-700 mb-2">
      {label}
    </label>
    {options ? (
      <select
        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        value={value}
        onChange={onChange}
        required={required}
      >
        <option value="">Select {label}</option>
        {options.map((option, index) => (
          <option key={index} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    ) : (
      <input
        type={type}
        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        value={value}
        onChange={onChange}
        required={required}
      />
    )}
  </div>
);

// Move TabButton component outside to prevent recreation on every render
const TabButton = ({ tab, label, isActive, onClick }) => (
  <button
    className={`px-6 py-3 rounded-lg font-medium transition-colors ${
      isActive
        ? "bg-blue-600 text-white"
        : "bg-gray-200 text-gray-700 hover:bg-gray-300"
    }`}
    onClick={onClick}
  >
    {label}
  </button>
);

const App = () => {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [customers, setCustomers] = useState([]);
  const [projects, setProjects] = useState([]);
  const [dashboardProjects, setDashboardProjects] = useState([]);
  const [expiringDomains, setExpiringDomains] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [projectDomains, setProjectDomains] = useState([]);
  const [domains, setDomains] = useState([]);
  const [amcProjects, setAmcProjects] = useState([]);
  const [editingItem, setEditingItem] = useState(null);
  const [editingType, setEditingType] = useState(null);

  // Form states
  const [customerForm, setCustomerForm] = useState({
    name: "",
    phone: "",
    email: "",
    address: ""
  });

  const [projectForm, setProjectForm] = useState({
    customer_id: "",
    type: "",
    name: "",
    amount: "",
    start_date: "",
    end_date: ""
  });

  const [domainForm, setDomainForm] = useState({
    project_id: "",
    domain_name: "",
    hosting_provider: "",
    username: "",
    password: "",
    validity_date: ""
  });

  // API calls
  const fetchCustomers = async () => {
    try {
      const response = await axios.get(`${API}/customers`);
      setCustomers(response.data);
    } catch (error) {
      console.error("Error fetching customers:", error);
    }
  };

  const fetchProjects = async () => {
    try {
      const response = await axios.get(`${API}/projects`);
      setProjects(response.data);
    } catch (error) {
      console.error("Error fetching projects:", error);
    }
  };

  const fetchDashboardProjects = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/projects`);
      setDashboardProjects(response.data);
    } catch (error) {
      console.error("Error fetching dashboard projects:", error);
    }
  };

  const fetchExpiringDomains = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/expiring-domains`);
      setExpiringDomains(response.data);
    } catch (error) {
      console.error("Error fetching expiring domains:", error);
    }
  };

  const fetchDomains = async () => {
    try {
      const response = await axios.get(`${API}/domains`);
      setDomains(response.data);
    } catch (error) {
      console.error("Error fetching domains:", error);
    }
  };

  const fetchProjectDomains = async (projectId) => {
    try {
      const response = await axios.get(`${API}/domains/project/${projectId}`);
      setProjectDomains(response.data);
    } catch (error) {
      console.error("Error fetching project domains:", error);
    }
  };

  const fetchAmcProjects = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/amc-projects`);
      setAmcProjects(response.data);
    } catch (error) {
      console.error("Error fetching AMC projects:", error);
    }
  };

  useEffect(() => {
    fetchCustomers();
    fetchProjects();
    fetchDashboardProjects();
    fetchExpiringDomains();
    fetchDomains();
    fetchAmcProjects();
  }, []);

  const handleCustomerSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/customers`, customerForm);
      setCustomerForm({ name: "", phone: "", email: "", address: "" });
      fetchCustomers();
      alert("Customer added successfully!");
    } catch (error) {
      console.error("Error adding customer:", error);
      alert("Error adding customer");
    }
  };

  const handleProjectSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/projects`, {
        ...projectForm,
        amount: parseFloat(projectForm.amount)
      });
      setProjectForm({
        customer_id: "",
        type: "",
        name: "",
        amount: "",
        start_date: "",
        end_date: ""
      });
      fetchProjects();
      fetchDashboardProjects();
      alert("Project added successfully!");
    } catch (error) {
      console.error("Error adding project:", error);
      alert("Error adding project");
    }
  };

  const handleDomainSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/domains`, domainForm);
      setDomainForm({
        project_id: "",
        domain_name: "",
        hosting_provider: "",
        username: "",
        password: "",
        validity_date: ""
      });
      fetchDashboardProjects();
      fetchExpiringDomains();
      if (selectedProject) {
        fetchProjectDomains(selectedProject);
      }
      alert("Domain/Hosting added successfully!");
    } catch (error) {
      console.error("Error adding domain:", error);
      alert("Error adding domain");
    }
  };

  const renderDashboard = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Dashboard Overview</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-blue-800">Total Customers</h3>
            <p className="text-3xl font-bold text-blue-600">{customers.length}</p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-green-800">Total Projects</h3>
            <p className="text-3xl font-bold text-green-600">{projects.length}</p>
          </div>
          <div className="bg-red-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-red-800">Expiring Domains</h3>
            <p className="text-3xl font-bold text-red-600">{expiringDomains.length}</p>
          </div>
        </div>

        {expiringDomains.length > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <h3 className="text-lg font-semibold text-red-800 mb-3">⚠️ Domains Expiring Soon</h3>
            <div className="space-y-2">
              {expiringDomains.map((domain, index) => (
                <div key={index} className="bg-white p-3 rounded border">
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="font-medium">{domain.domain_name}</p>
                      <p className="text-sm text-gray-600">
                        {domain.customer_name} - {domain.project_name}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-red-600 font-medium">
                        Expires: {new Date(domain.validity_date).toLocaleDateString()}
                      </p>
                      <p className="text-xs text-red-500">
                        {domain.days_remaining} days remaining
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="overflow-x-auto">
          <table className="w-full table-auto">
            <thead>
              <tr className="bg-gray-50">
                <th className="px-4 py-2 text-left">Customer</th>
                <th className="px-4 py-2 text-left">Project</th>
                <th className="px-4 py-2 text-left">Type</th>
                <th className="px-4 py-2 text-left">Amount</th>
                <th className="px-4 py-2 text-left">Duration</th>
                <th className="px-4 py-2 text-left">Domains</th>
              </tr>
            </thead>
            <tbody>
              {dashboardProjects.map((project) => (
                <tr key={project.id} className="border-b">
                  <td className="px-4 py-2">
                    <div>
                      <p className="font-medium">{project.customer_name}</p>
                      <p className="text-sm text-gray-600">{project.customer_email}</p>
                    </div>
                  </td>
                  <td className="px-4 py-2 font-medium">{project.name}</td>
                  <td className="px-4 py-2">{project.type}</td>
                  <td className="px-4 py-2">${project.amount.toLocaleString()}</td>
                  <td className="px-4 py-2">
                    <div className="text-sm">
                      <p>{new Date(project.start_date).toLocaleDateString()}</p>
                      <p>{new Date(project.end_date).toLocaleDateString()}</p>
                    </div>
                  </td>
                  <td className="px-4 py-2">
                    <div className="space-y-1">
                      {project.domains.map((domain, index) => (
                        <div key={index} className="text-sm">
                          <p className="font-medium">{domain.domain_name}</p>
                          <p className="text-gray-600">{domain.hosting_provider}</p>
                        </div>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderCustomerForm = () => (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Add New Customer</h2>
      <form onSubmit={handleCustomerSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormInput
            label="Customer Name"
            value={customerForm.name}
            onChange={(e) => setCustomerForm({ ...customerForm, name: e.target.value })}
          />
          <FormInput
            label="Phone Number"
            type="tel"
            value={customerForm.phone}
            onChange={(e) => setCustomerForm({ ...customerForm, phone: e.target.value })}
          />
          <FormInput
            label="Email Address"
            type="email"
            value={customerForm.email}
            onChange={(e) => setCustomerForm({ ...customerForm, email: e.target.value })}
          />
          <FormInput
            label="Address"
            value={customerForm.address}
            onChange={(e) => setCustomerForm({ ...customerForm, address: e.target.value })}
          />
        </div>
        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
        >
          Add Customer
        </button>
      </form>
    </div>
  );

  const renderProjectForm = () => (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Add New Project</h2>
      <form onSubmit={handleProjectSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormInput
            label="Customer"
            value={projectForm.customer_id}
            onChange={(e) => setProjectForm({ ...projectForm, customer_id: e.target.value })}
            options={customers.map(customer => ({
              value: customer.id,
              label: `${customer.name} - ${customer.email}`
            }))}
          />
          <FormInput
            label="Project Type"
            value={projectForm.type}
            onChange={(e) => setProjectForm({ ...projectForm, type: e.target.value })}
          />
          <FormInput
            label="Project Name"
            value={projectForm.name}
            onChange={(e) => setProjectForm({ ...projectForm, name: e.target.value })}
          />
          <FormInput
            label="Project Amount"
            type="number"
            value={projectForm.amount}
            onChange={(e) => setProjectForm({ ...projectForm, amount: e.target.value })}
          />
          <FormInput
            label="Start Date"
            type="date"
            value={projectForm.start_date}
            onChange={(e) => setProjectForm({ ...projectForm, start_date: e.target.value })}
          />
          <FormInput
            label="End Date"
            type="date"
            value={projectForm.end_date}
            onChange={(e) => setProjectForm({ ...projectForm, end_date: e.target.value })}
          />
        </div>
        <button
          type="submit"
          className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition-colors"
        >
          Add Project
        </button>
      </form>
    </div>
  );

  const renderDomainForm = () => (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Add Domain/Hosting</h2>
      <form onSubmit={handleDomainSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormInput
            label="Project"
            value={domainForm.project_id}
            onChange={(e) => setDomainForm({ ...domainForm, project_id: e.target.value })}
            options={projects.map(project => ({
              value: project.id,
              label: `${project.name} - ${project.type}`
            }))}
          />
          <FormInput
            label="Domain Name"
            value={domainForm.domain_name}
            onChange={(e) => setDomainForm({ ...domainForm, domain_name: e.target.value })}
          />
          <FormInput
            label="Hosting Provider"
            value={domainForm.hosting_provider}
            onChange={(e) => setDomainForm({ ...domainForm, hosting_provider: e.target.value })}
          />
          <FormInput
            label="Username"
            value={domainForm.username}
            onChange={(e) => setDomainForm({ ...domainForm, username: e.target.value })}
          />
          <FormInput
            label="Password"
            type="password"
            value={domainForm.password}
            onChange={(e) => setDomainForm({ ...domainForm, password: e.target.value })}
          />
          <FormInput
            label="Validity Date"
            type="date"
            value={domainForm.validity_date}
            onChange={(e) => setDomainForm({ ...domainForm, validity_date: e.target.value })}
          />
        </div>
        <button
          type="submit"
          className="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 transition-colors"
        >
          Add Domain/Hosting
        </button>
      </form>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-8">Agency Management System</h1>
        
        <div className="flex flex-wrap gap-4 mb-8">
          <TabButton
            tab="dashboard"
            label="Dashboard"
            isActive={activeTab === "dashboard"}
            onClick={() => setActiveTab("dashboard")}
          />
          <TabButton
            tab="customers"
            label="Add Customer"
            isActive={activeTab === "customers"}
            onClick={() => setActiveTab("customers")}
          />
          <TabButton
            tab="projects"
            label="Add Project"
            isActive={activeTab === "projects"}
            onClick={() => setActiveTab("projects")}
          />
          <TabButton
            tab="domains"
            label="Add Domain/Hosting"
            isActive={activeTab === "domains"}
            onClick={() => setActiveTab("domains")}
          />
        </div>

        {activeTab === "dashboard" && renderDashboard()}
        {activeTab === "customers" && renderCustomerForm()}
        {activeTab === "projects" && renderProjectForm()}
        {activeTab === "domains" && renderDomainForm()}
      </div>
    </div>
  );
};

export default App;